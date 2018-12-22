urlDict = {1:'/',
           2:'/blogs',
           3:'/imarket'}
def getUrl(linkId):
    url = urlDict[linkId]
    if not url:
        return urlDict[1]
    else:
        return url
