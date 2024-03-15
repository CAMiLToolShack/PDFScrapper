from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import os

pages = []


def remove_empty_lines(string):
    lines = string.splitlines()
    non_empty_lines = [line for line in lines if line.strip() != ""]
    string_without_empty_lines = "\n".join(non_empty_lines)
    string_without_empty_lines = string_without_empty_lines.encode("ascii", "ignore").decode()  # Ignore non-ASCII characters
    return string_without_empty_lines


def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()
    pagesOfText = [text]
    for i in range(len(pagesOfText)):
        pagesOfText[i] = remove_empty_lines(pagesOfText[i])
    fp.close()
    device.close()
    retstr.close()
    return pagesOfText


def get_text_to_newline(text, start_index):
    while text[start_index - 1]  != '\n':
        start_index -= 1
    end_index = text.find('\n', start_index)
    if end_index == -1:  # If no new line is found, get the rest of the string
        return text[start_index:]
    else:
        return text[start_index:end_index]


def remove_lines_at_target(string, target):
    if target == "":
        return string
    if target.find('\n') == -1:
        lines = string.splitlines()
        lines = [line for line in lines if target not in line]
        return '\n'.join(lines)
    else:
        targetLines = target.splitlines()
        lines = string.splitlines()
        for targetLine in targetLines:
            if targetLine == "- ":
                continue
            lines = [line for line in lines if targetLine not in line]
        return '\n'.join(lines)


def findWithList(string, lst):
    result = []
    string = string.lower()  # Convert string to lowercase
    for i, item in enumerate(lst):
        item = item.lower()  # Convert list item to lowercase
        if string.find(item) != -1:
            result.append(item)
    return result

def getContactInformation():
    contactInformation = []
    organizationName = "Organization: "
    website = "Website: "
    while pages[0].find("Name:") != -1:  # gets the name emails and phone numbers attached to the document
        indexOfName = pages[0].find("Name:")
        if indexOfName != -1:
            indexOfEmail = pages[0].find("Email:", indexOfName)
            indexOfPhone = pages[0].find("Phone:", indexOfEmail)
            name = get_text_to_newline(pages[0], indexOfName)
            email = get_text_to_newline(pages[0], indexOfEmail)
            phone = get_text_to_newline(pages[0], indexOfPhone)
            contactInformation.append([name, email, phone])
            pages[0] = remove_lines_at_target(pages[0], name)
            pages[0] = remove_lines_at_target(pages[0], email)
            pages[0] = remove_lines_at_target(pages[0], phone)
    pages[0] = remove_lines_at_target(pages[0], "Contact Information")

    if len(findWithList(pages[0], [".com", ".org", ".net", ".edu", ".gov"])) > 0:
        indexOfOrganizationWebiste = pages[0].find(".")
        websiteInfo = get_text_to_newline(pages[0], indexOfOrganizationWebiste)
        pages[0] = remove_lines_at_target(pages[0], websiteInfo)
        website += websiteInfo


    if pages[0].find("Organization") != -1:
        indexOfOrganization = pages[0].find("Organization")
        pages[0] = remove_lines_at_target(pages[0], "Organization")
        indexOfOrganizationEnd = pages[0].find("Project Overview")
        if indexOfOrganizationEnd == -1:
            indexOfOrganizationEnd = pages[0].find("Activity Description")
        organizationNameInfo = pages[0][indexOfOrganization:indexOfOrganizationEnd]
        pages[0] = remove_lines_at_target(pages[0], organizationNameInfo)
        organizationName += organizationNameInfo.replace('\n', '')

    contactInformation.append([organizationName, website])
    pages[0] = remove_lines_at_target(pages[0], "Points of Contact")

    return contactInformation


def getProjectOverview():
    projectOverview = []
    description = "Description: "
    pages[0] = remove_lines_at_target(pages[0], "Project Overview")
    pages[0] = remove_lines_at_target(pages[0], "Activity Description")
    indexOfDescription = pages[0].find("Description")
    pages[0] = remove_lines_at_target(pages[0], "Description")
    indexOfOperationalNeed = pages[0].find("Operational Need")
    descriptionInfo = pages[0][indexOfDescription:indexOfOperationalNeed]
    pages[0] = remove_lines_at_target(pages[0], descriptionInfo)
    description += descriptionInfo.replace('\n', '')

    OperationalNeed = "Operational Need: "
    indexOfOperationalNeed = pages[0].find("Operational Need")
    pages[0] = remove_lines_at_target(pages[0], "Operational Need")
    indexOfOperationalNeedEnd = pages[0].find("Objectives")
    OperationalNeedInfo = pages[0][indexOfOperationalNeed:indexOfOperationalNeedEnd]
    pages[0] = remove_lines_at_target(pages[0], OperationalNeedInfo)
    OperationalNeed += OperationalNeedInfo.replace('\n', '')

    objectives = "Objectives: "
    indexOfObjectives = pages[0].find("Objectives")
    pages[0] = remove_lines_at_target(pages[0], "Objectives")
    indexOfObjectivesEnd = pages[0].find("Systems Under Test")
    objectivesInfo = pages[0][indexOfObjectives:indexOfObjectivesEnd]
    pages[0] = remove_lines_at_target(pages[0], objectivesInfo)
    objectives += objectivesInfo.replace('\n', '')
    objectives = objectives.replace('-', '\n')

    projectOverview.append([description, OperationalNeed, objectives])
    return projectOverview


def getSystemsUnderTest():
    systemsUnderTest = []
    indexOfSystemsUnderTest = pages[0].find("Systems Under Test")
    pages[0] = remove_lines_at_target(pages[0], "Systems Under Test")
    systemsUnderTestInfo = pages[0][indexOfSystemsUnderTest:len(pages[0]) - 1]
    pages[0] = remove_lines_at_target(pages[0], systemsUnderTestInfo)
    systemsUnderTest.append("Systems Under Test: " + systemsUnderTestInfo.replace('\n', ''))
    return systemsUnderTest



def getSupportingResources():
    supportingResources = []
    if pages[0].find("Supporting Resources") != -1:
        indexOfSupportingResources = pages[0].find("Supporting Resources")
        indexOfSupportingResourcesEnd = pages[0].find("Participants")
        if indexOfSupportingResourcesEnd == -1:
            indexOfSupportingResourcesEnd = len(pages[0]) - 1
        supportingResourcesInfo = pages[0][indexOfSupportingResources:indexOfSupportingResourcesEnd]
        pages[0] = remove_lines_at_target(pages[0], supportingResourcesInfo)
        supportingResources.append(supportingResourcesInfo.replace('\n', ''))
        if indexOfSupportingResourcesEnd != -1:
            indexOfParticipants = pages[0].find("Participants")
            participantsInfo = pages[0][indexOfParticipants:len(pages[0]) - 1]
            pages[0] = remove_lines_at_target(pages[0], participantsInfo)
            supportingResources.append(participantsInfo.replace('\n', ''))
        return supportingResources


def getRequiredApprovals():
    requiredApprovals = []
    requiredApprovalsStart = pages[0].find("Does your system use lithium batteries? If so, please describe the batteries in terms of quantity")
    if requiredApprovalsStart != -1:
        requiredApprovalsEnd = pages[0].find("provisional until emitter information has been submitted to the ANTX-CT23 planning team.")
        requiredApprovalsInfo = pages[0][requiredApprovalsStart:requiredApprovalsEnd]
        pages[0] = remove_lines_at_target(pages[0], requiredApprovalsInfo)
        pages[0] = remove_lines_at_target(pages[0], "Required Approvals")
        requiredApprovals.append("Required Approvals: " + requiredApprovalsInfo.replace('\n', ''))
        return requiredApprovals

def printContactInformation():
    contactInformation = getContactInformation()
    for i in range(len(contactInformation)):
        print(contactInformation[i])


def printProjectOverview():
    projectOverview = getProjectOverview()
    for i in range(len(projectOverview)):
        print(projectOverview[i])


def clean():
    for i in range(len(pages)):
        pages[i] = pages[i].replace("\uf0b7","-")
        pages[i] = pages[i].replace("\u2022","-")
    undesirableStrings = ["ANTX-Coastal Trident", "Program Summary and After Action Report",
                          "Advanced Naval Technology Exercise Program", "Request for Project Proposals",
                          "Request for Project Information", "Request of Project Infromation"]
    removeListOfStrings(undesirableStrings)




def removeListOfStrings(lst):
    for item in lst:
        pages[0] = remove_lines_at_target(pages[0], item)


def writeListToFile(lst, file):
    if lst.__class__ == list:
        for i in range(len(lst)):
            if lst[i].__class__ == list:
                for j in range(len(lst[i])):
                    file.write(lst[i][j] + "\n")
                file.write("\n")
            else:
                file.write(lst[i] + "\n")
    else:
        file.write("\n")


def read_files_in_directory(directory_path):
    files = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):  # specify the type of file you're looking for
            files.append(filename)
    return files


def get_current_directory():
    return os.path.dirname(os.path.realpath(__file__))


currentDirectory = get_current_directory()
files = read_files_in_directory(currentDirectory + "\\inputs")
for file in files:
    with open (currentDirectory + "\\outputs\\" + file[:-4] + ".txt", "w") as text_file:
        pages = convert_pdf_to_txt(currentDirectory + "\\inputs\\" + file)
        print(file)
        clean()
        contactInformation = getContactInformation()
        projectOverview = getProjectOverview()
        supportingResources = getSupportingResources()
        requiredApprovals = getRequiredApprovals()
        systemsUnderTest = getSystemsUnderTest()
        writeListToFile(contactInformation, text_file)
        writeListToFile(projectOverview, text_file)
        writeListToFile(supportingResources, text_file)
        writeListToFile(systemsUnderTest, text_file)
        writeListToFile(requiredApprovals, text_file)

