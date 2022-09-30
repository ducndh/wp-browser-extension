chrome.tabs.onUpdated.addListener((tabId, tab) => {
    if (tab.url && tab.url.includes(".wikipedia.org/wiki/")) {
      const queryParameters = tab.url.split("/")[1];
      const urlParameters = new URLSearchParams(queryParameters);
  
      chrome.tabs.sendMessage(tabId, {
        type: "NEW",
        wikiTitle: urlParameters.get("v"),
      });
    }
  });