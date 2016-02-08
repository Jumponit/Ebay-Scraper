
chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        switch (request.directive) {
        case "popup-click":
            // execute the content script
            chrome.tabs.executeScript(null, { // defaults to the current tab
                file: "contentscript.js", // script to inject into page and run in sandbox
                allFrames: true // This injects script into iframes in the page and doesn't work before 4.0.266.0.
            });
            sendResponse({}); // sending back empty response to sender
            break;
        default:
            // helps debug when request directive doesn't match
            alert("Unmatched request of '" + request + "' from script to background.js from " + sender);
        }
    }
);

function resetDefaultSuggestion() {
	  chrome.omnibox.setDefaultSuggestion({
	  description: 'eps: Search ebay for past price history for: %s'
	  });
	}
	resetDefaultSuggestion();function resetDefaultSuggestion() {
	  chrome.omnibox.setDefaultSuggestion({
	  description: 'eps: Search ebay for past price history for: %s'
	  });
	}
	resetDefaultSuggestion();
	
function navigate(url) {
	  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
	  chrome.tabs.update(tabs[0].id, {url: url});
	  });
	}
chrome.omnibox.onInputEntered.addListener(function(text) {
	  navigate("http://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313.TR12.TRC2.A0.H0.Xsearch.TRS0&_nkw=" + text);
	});
