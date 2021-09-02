import requests, firebase_admin
from bs4 import BeautifulSoup
from firebase_admin import credentials
from firebase_admin import firestore
import time, json

credential = credentials.Certificate('private.json')
firebase_admin.initialize_app(credential)
db = firestore.client()

# Change This Collection Name
collection = db.collection("xd")

collectionCounter = 0

finalList = []
totalCount = 0
errorCount = 0
skipCount = 0
addedCount = 0

def checkIfNotBlocked(pageResponse):
    page = BeautifulSoup(pageResponse.text, "lxml").findAll('p')
    for item in page:
        if item.getText() == "Bot Protection Firewall":
            return True
    return False

def GoToLink(page, category):
    global collectionCounter
    global totalCount
    global errorCount
    global skipCount
    global addedCount
    
    ui = BeautifulSoup(page.text, "lxml").findAll('article', class_='blog-non-single-post')
    if checkIfNotBlocked(page):
        print("--------- BLOCKED US (AT 1st PAGE) ---------")
        return
    
    # Iterating Over Each Article
    for item in ui:
        try:
            # Default Values
            imageUrl = ""
            source = ""
            title = ""
            author = ""
            downloadUrl = ""
            fileName = ""
            tag = []
            timeStamp = ""
            uiImages = []

            # Get Main Image URL.
            imageUrl = item.find('div', class_='blog-post-img img-loading').a.img
            if "https://" in imageUrl['src']:
                imageUrl = imageUrl['src']
                
            elif "https://" in imageUrl['data-lazy-src']:
                imageUrl = imageUrl['data-lazy-src']

            if "520x281" in imageUrl:
                imageUrl = imageUrl.replace("520x281", "1014x487")

            # Get Next Page URL to Iterate Upon.
            source = item.find('div', class_='blog-post-img img-loading').a['href']

            # Get Title for the UI Recipe.
            title = item.find('h2', class_='post-title entry-title').a.getText().strip()

            # Going to next Page in XD Guru.
            go = requests.get(source)
            nextPage = BeautifulSoup(go.text, "lxml").find('div', class_='content')

            if checkIfNotBlocked(go):
                print("--------- BLOCKED US (AT 2nd PAGE) ---------")
                return
            
            # Fetching Author From XD Guru.
            author = nextPage.find('div', class_='entry-content').a.getText().strip()

            # FileName Same as Title replacing spaces by Hypens.
            fileName = title.replace(" ", "_") + ".xd".strip()

            # Getting Current TimeStamp.
            timeStamp = time.time()

            # Go To Page For Tags and Download Links.
            getItNowButton = nextPage.find('a', class_='button')
            if getItNowButton is not None:
                getItNowButton = getItNowButton['href']
            else:
                continue

            # Checking Download Options.
            goToExternalLinks = ""

            # Default Tags For UI Recipe.
            tag.append(author)
            tag.append(title)
                    
            if "behance.net" in getItNowButton:
                    
                # Going to Behance Page.
                requestBehancePage = requests.get(getItNowButton)

                # Fething all Links from the Page.
                goToExternalLinks = BeautifulSoup(requestBehancePage.text, "lxml").findAll('a', class_='ProjectTags-tagLink-Hh_')
                allPossibleDownloadLinks = BeautifulSoup(requestBehancePage.text, "lxml").findAll('a')

                # List of All Links from Behance Page.
                links = []
                for link in allPossibleDownloadLinks:
                    links.append(link.get('href'))

                # Getting Download Link From Behance.
                for singleDownload in links:
                    if "dropbox.com" in str(singleDownload):
                        downloadUrl = singleDownload.replace("?dl=0", "?dl=1")

                # Getting All Tags From Behance Page.
                totalTags = goToExternalLinks
                    
                for tagItem in totalTags:
                    tag.append(tagItem.getText().strip())

                # Getting All Images From The Behance Page.
                possibleImages = BeautifulSoup(requestBehancePage.text, "lxml").findAll('img', class_='ImageElement-image-2K6')

                for singleImage in possibleImages:
                    uiImages.append(singleImage.get('src'))
                        
            elif "dribbble.com" in getItNowButton:

                # Going to Dribbble Page.
                requestDribbblePage = requests.get(getItNowButton)
                goToExternalLinks = BeautifulSoup(requestDribbblePage.text, "lxml").find('div', class_='download-row')

                # Getting Download Link From Dribbble.
                downloadUrl = "https://dribbble.com" + goToExternalLinks.find('a', class_='download-link form-btn outlined')['href']

                possibleImages = BeautifulSoup(requestDribbblePage.text, "lxml").findAll('img', class_='lrg-16x12')

                for singleImage in possibleImages:
                    resizedImage = singleImage.get('src').replace('?compress=1&resize=400x300', '')
                    uiImages.append(resizedImage)

            if len(uiImages) == 0:
                uiImages.append(imageUrl)

            # Skip UI which doesn't have Download Url or Author Name
            if (author != "") and downloadUrl != "":
                final = {
                'author': author,
                'category': category,
                'downloadUrl': downloadUrl,
                'fileName': fileName,
                'imageUrl': imageUrl,
                'source': source,
                'tag': tag,
                'timeStamp': timeStamp,
                'title': title,
                'uiImages': uiImages
                }

                if inputGoesHere == 'WRITE':
                    finalList.append(final)
                else:
                    collection.add(final)
                    collectionCounter = collectionCounter + 1
                    print("XD -> " + str(collectionCounter))

                addedCount = addedCount + 1

            else:
                skipCount = skipCount + 1
                print("Skip Occured.")
                    
        except AttributeError:
            errorCount = errorCount + 1
            print("\nError Occured.")

        totalCount = totalCount + 1
        print("Total Scrap = " + str(totalCount) + " Error = " + str(errorCount) + " Skip = " + str(skipCount) + " Added = " + str(addedCount))


def fetchUIRelatedPage(inputUIToFetch, start, end):
    baseUrl = ""
    page_count = start
    pageCategory = ""
    
    if inputUIToFetch == "Website":
        baseUrl = "https://www.figmacrush.com/xd-website-templates/page/"
        pageCategory = "Website"
        
    elif inputUIToFetch == "Mobile":
        baseUrl = "https://www.figmacrush.com/xd-mobile-templates/page/"
        pageCategory = "Mobile"
        
    elif inputUIToFetch == "Miscellaneous":
        baseUrl = "https://www.figmacrush.com/xd-misc-ui/page/"
        pageCategory = "Miscellaneous"
        
    elif inputUIToFetch == "UI Kits":
        baseUrl = "https://www.figmacrush.com/free-xd-ui-kits/page/"
        pageCategory = "Miscellaneous"
        
    elif inputUIToFetch == "Wireframes":
        baseUrl = "https://www.figmacrush.com/adobe-xd-wireframe-kits/page/"
        pageCategory = "Miscellaneous"
        
    elif inputUIToFetch == "Icons":
        baseUrl = "https://www.figmacrush.com/adobe-xd-icons/page/"
        pageCategory = "Miscellaneous"
        
    elif inputUIToFetch == "Illustrations":
        baseUrl = "https://www.figmacrush.com/adobe-xd-illustrations-vectors/page/"
        pageCategory = "Miscellaneous"
        
    elif inputUIToFetch == "Animations":
        baseUrl = "https://www.figmacrush.com/xd-animation-templates/page/"
        pageCategory = "Miscellaneous"
        
    else:
        print("Not a Valid Input is Given.")

    while True:
        pageUrlWebsite = baseUrl + str(page_count) + '/'
        page = requests.get(pageUrlWebsite)
        #if page.status_code == 200:
        if page_count != end+1:
            print("\n" + inputUIToFetch + " Page Number = "  + str(page_count))
            GoToLink(page, pageCategory)    
            page_count += 1
        else:
            break

def ReadAndStore():
    global collectionCounter
    
    with open("xd.json", "r") as readMyFile:
        myData = json.load(readMyFile)
    
        for singleData in myData:
            collection.add(singleData)
            collectionCounter = collectionCounter + 1
            print("Inserted -> " + str(collectionCounter))

        print("---------Insertion Completes Here---------")
    

inputGoesHere = "READ" # READ or FETCH or WRITE

if inputGoesHere == "READ":
    ReadAndStore()
else:
    
    inputUIToFetch = "Website" # Website, Mobile, Miscellaneous, UI Kits, Wireframes, Icons, Illustrations, Animations
    fetchUIRelatedPage(inputUIToFetch,1, 5)
    
    if inputGoesHere == 'WRITE':
        with open("xd.json", "w") as writeMyFile:
            json.dump(finalList, writeMyFile)
