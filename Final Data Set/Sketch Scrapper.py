import requests, firebase_admin
from bs4 import BeautifulSoup
from firebase_admin import credentials
from firebase_admin import firestore
import time, json

credential = credentials.Certificate('private.json')
firebase_admin.initialize_app(credential)
db = firestore.client()

# Change This Collection Name
collection = db.collection("sketch")

collectionCounter = 0

finalList = []
totalCount = 0
errorCount = 0
skipCount = 0
addedCount = 0

def GoToLink(page, category):
    global collectionCounter
    global totalCount
    global errorCount
    global skipCount
    global addedCount
    
    ui = BeautifulSoup(page.text, "lxml").findAll('div', class_='module-list')
    
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

            # Get Next Page URL to Iterate Upon.
            source = "https://www.sketchappsources.com" + item.a['href']

            # Get Title for the UI Recipe.
            title = item.span.getText().strip()

            # Going to next Page For More Details.
            numberOfRetries = 0
            go = ""
            while go == "":
                numberOfRetries += 1
                
                try:
                    go = requests.get(source)
                    break
                except:
                    if numberOfRetries > 2:
                        break
                    time.sleep(1)
                    continue
                
            nextPage = BeautifulSoup(go.text, "lxml").find('article', class_='source')

            # Get Main Image URL.
            imageUrl = "https://www.sketchappsources.com" + nextPage.find('figure', class_='zoom').img['src']
            
            # Fetching Author.
            author = nextPage.find('p', class_='source-author').a.getText().strip()

            # FileName Same as Title replacing spaces by Hypens.
            fileName = title.replace(" ", "_") + ".zip".strip()

            # Getting Current TimeStamp.
            timeStamp = time.time()

            # Getting Download Link.
            downloadUrl = "https://www.sketchappsources.com" + nextPage.find('div', class_='source-details').a['href']

            # Go To Page For Tags and uiImages.
            finalPage = ""
            authorPage = nextPage.findAll('a', class_='source-author-plus')
            for singleLink in authorPage:
                if singleLink is not None:
                    finalPage = singleLink['href']
                else:
                    continue

            if "dribbble.com" in finalPage:
                # Going to Dribbble Page.
                requestDribbblePage = ""
                while requestDribbblePage == "":
                    try:
                        requestDribbblePage = requests.get(finalPage)
                        break
                    except:
                        time.sleep(5)
                        continue

                # Get all possible Images
                possibleImages = BeautifulSoup(requestDribbblePage.text, "lxml").findAll('img', class_='lrg-16x12')
                
                for singleImage in possibleImages:
                    resizedImage = singleImage.get('src').replace('?compress=1&resize=400x300', '')
                    uiImages.append(resizedImage)

            if len(uiImages) == 0:
                uiImages.append(imageUrl)

            tag.append(author)
            tag.append(title)
                
            tagsTop = nextPage.find('p', class_='tags-top').findAll('a')
            for singleTag in tagsTop:
                tag.append(singleTag.getText().strip())

            tagsBottom = nextPage.find('p', class_='tags-bottom').findAll('a')
            for singleTag in tagsBottom:
                tag.append(singleTag.getText().strip())        

            # Skip UI which doesn't have Author Name.
            if (author != ""):
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
                    print("Sketch -> " + str(collectionCounter))

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
        # Change Manually
        #baseUrl = "https://www.sketchappsources.com/tag/web.html?"
        #baseUrl = "https://www.sketchappsources.com/category/desktop.html?"
        pageCategory = "Website"
        
    elif inputUIToFetch == "Mobile":
        baseUrl = "https://www.sketchappsources.com/category/mobile.html?"
        pageCategory = "Mobile"
        
    elif inputUIToFetch == "Miscellaneous":
        # Change Manually
        baseUrl = "https://www.sketchappsources.com/tag/ecommerce.html?"
        #baseUrl = "https://www.sketchappsources.com/tag/social.html?"
        #baseUrl = "https://www.sketchappsources.com/tag/concept.html?"
        pageCategory = "Miscellaneous"
        
    elif inputUIToFetch == "UI Kits":
        # Change Manually
        baseUrl = "https://www.sketchappsources.com/category/ui.html?"
        #baseUrl = "https://www.sketchappsources.com/tag/kit.html?"
        #baseUrl = "https://www.sketchappsources.com/tag/android.html?"
        #baseUrl = "https://www.sketchappsources.com/tag/ios.html?"
        pageCategory = "Miscellaneous"
        
    elif inputUIToFetch == "Wireframes":
        baseUrl = "https://www.sketchappsources.com/category/wireframe.html?"
        pageCategory = "Miscellaneous"
        
    elif inputUIToFetch == "Icons":
        baseUrl = "https://www.sketchappsources.com/category/icon.html?"
        pageCategory = "Miscellaneous"
        
    elif inputUIToFetch == "Illustrations":
        baseUrl = "https://www.sketchappsources.com/tag/illustration.html?"
        pageCategory = "Miscellaneous"
        
    elif inputUIToFetch == "Animations":
        baseUrl = "https://www.sketchappsources.com/category/real.html?"
        pageCategory = "Miscellaneous"
        
    else:
        print("Not a Valid Input is Given.")

    while True:
        pageUrlWebsite = baseUrl + str(page_count)
        page = ""
        while page == "":
            try:
                page = requests.get(pageUrlWebsite)
                break
            except:
                time.sleep(5)
                continue
            
        #if page.status_code == 200:
        if page_count != end+1:
            print("\n" + inputUIToFetch + " Page Number = "  + str(page_count))
            GoToLink(page, pageCategory)
            page_count += 1
        else:
            break

def ReadAndStore():
    global collectionCounter
    
    with open("sketch.json", "r") as readMyFile:
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
    
    inputUIToFetch = "Animations" # Website, Mobile, Miscellaneous, UI Kits, Wireframes, Icons, Illustrations, Animations
    fetchUIRelatedPage(inputUIToFetch, 1, 15)
    
    if inputGoesHere == 'WRITE':
        with open("sketch.json", "w") as writeMyFile:
            json.dump(finalList, writeMyFile)
