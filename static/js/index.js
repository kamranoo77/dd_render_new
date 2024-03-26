const msgerInput = get(".msger-input");
const msger = document.querySelector(".msger");
const msgerChat = get(".msger-chat");
const BOT_IMG = "/static/icons/bot.svg";
const PERSON_IMG = "/static/icons/user.svg";
const BOT_NAME = "AI.";
const PERSON_NAME = "User";
let mediaRecorder;
let isRecording = false;
let audioChunks = [];
const blobs = document.getElementById("blobs");
let uniqueIdCounter = 0;
const chatBox = document.querySelector(".msger-chat");
const queryInput = document.getElementById("queryForm");
let svg = getSVG();
const chatScreen = document.querySelector(".msger-chat");
var buttons = document.getElementsByClassName("button");
const loading = getloadingSvg();
const queryString = window.location.search;
const userText = document.querySelector(".User");
const botText = document.querySelector(".JobBot");
const fastText = document.querySelector(".toggleFast");
let transJobBot = "";
let transUser = "";
let transPlaceholder = "";
let transFast = "";
let transSlow = "";
let transgroq = "";
let transFeedback = "";
let transIntromessage = "";
let transBtn = "";
let transSubmit = "";
let transClose = "";
let fastBtn = document.getElementById("fast");
let slowBtn = document.getElementById("slow");
let groqBtn = document.getElementById("groq");
const interfaceSound = "/static/sounds/interface.mp3";
const bubbleSound = "/static/sounds/bubble.mp3";
const voiceSound = "/static/sounds/audio.mp3";
const submitSound = "/static/sounds/submit.mp3";
const standardSound = "/static/sounds/click.mp3";
const msgsound = "/static/sounds/standard.mp3";
const toggle = "/static/sounds/switch.mp3";
let fastImg = `<img class='textImg' src="/static/icons/gptFast.svg" alt="fastGPT"  />`;
fastBtn.checked = true;
fastText.innerHTML = fastImg;
let modalView = true;
const urlParams = new URLSearchParams(queryString);
const query = urlParams.get("q");
const leng = urlParams.get("leng");
let isPlay = true;
let titleOfPage = document.getElementById("titleOfPage");
let audio = new Audio();

let iscompleted = true;
let questionsList = [];
let questionIndex = 0;
let questionsAndAnswers = [];
let responseReceived = null;
let currentAns = null;
let currentQues = null;
let questionFlag = false;



function removeNumericPrefix(inputString) {
  let startIndex = 0;
  for (let i = 0; i < inputString.length; i++) {
      const char = inputString[i];
      if (char >= '0' && char <= '9' || char === '.') {
          startIndex = i + 1;
      } else {
          break;
      }
  }
  return inputString.substring(startIndex);
}

function fetchTranslations() {
  fetch("/trans")
    .then((response) => response.json())
    .then((data) => {
      msgerInput.placeholder = data[2];
      transPlaceholder = data[2];
      transFast = data[4];
      transUser = data[1];
      transJobBot = data[0];
      titleOfPage.innerText = data[0];
      transFeedback = data[3];
      transIntromessage = data[5];
      transBtn = data[6];
      transSubmit = data[7];
      transClose = data[8];
      document.title = data[0];
      transSlow = data[9];
      transgroq = data[10];
      appendMessage(transJobBot, BOT_IMG, "left", transIntromessage);
      if (query || leng) {
        const fast = fastBtn.checked || false;
        const slow = slowBtn.checked || false;
        const groq = groqBtn.checked || false;
        handleSubmitButton(query, fast, slow, groq, leng);
      }
    })
    .catch((error) => console.error("Error:", error));
}

fetchTranslations();

function appendMessage(name, img, side, text) {
  const uniqueId = generateUniqueId();

  // Only include buttons for messages on the left side
  let buttonsHTML = "";
  if (side === "left") {
    buttonsHTML = `
          <div class="msg-buttons">
              <button onclick="sendFeedback('${uniqueId}', 'up')">👍</button>
              <button onclick="sendFeedback('${uniqueId}', 'down')">👎</button>
              <button class='texFeedback' onclick="openFeedbackWindow('${uniqueId}')">${transFeedback}</button>
          </div>
      `;
  }

  // Message HTML
  const msgHTML = `
      <div class="${side}Msgbox ${side}_animation">
          <div class="msg ${side}-msg">
              <div class="msg-img">
                  <img src="${img}" />
              </div>
              <div class="msg-bubble">
                  <div class="msg-info">
                      <div class="msg-info-name ${name}">${name}</div>
                      <div class="msg-info-time">${formatDate(new Date())}</div>
                  </div>
                  <div class="msg-text" data-id="${
                    side === "left" ? uniqueId : ""
                  }">${text}</div>
                  ${buttonsHTML}  <!-- Buttons included conditionally -->
              </div>
          </div>
      </div>
  `;

  msgerChat.insertAdjacentHTML("beforeend", msgHTML);
  msgerChat.scrollTop += 500;
}

// Function to handle feedback button clicks
function openFeedbackWindow(uniqueId) {
  const feedbackWindowHTML = `
    <div class="feedback-window" id="feedbackWindow_${uniqueId}">
    <h2>${transFeedback}</h2>
     <div>
     <textarea placeholder=${transFeedback} id="feedbackText_${uniqueId}"></textarea>
     <br/>
     <button onclick="submitFeedback('${uniqueId}')">${transSubmit}</button>
     <button onclick="closeFeedbackWindow('${uniqueId}')">${transClose}</button>
     </div>
    </div>
  `;
  document.body.insertAdjacentHTML("beforeend", feedbackWindowHTML);
}

function closeFeedbackWindow(uniqueId) {
  document.getElementById(`feedbackWindow_${uniqueId}`).remove();
}

function sendFeedback(uniqueId, type) {
  playSoundEffect(standardSound);
  sendToFlask("/feedback", {
    uniqueId,
    type,
    l2ResponseClicked,
    l3ResponseClicked,
  });
}

function submitFeedback(uniqueId) {
  playSoundEffect(standardSound);
  const feedbackText = document.getElementById(
    `feedbackText_${uniqueId}`
  ).value;
  sendToFlask("/feedback", {
    uniqueId,
    feedback: feedbackText,
    l2ResponseClicked,
    l3ResponseClicked,
  });
  closeFeedbackWindow(uniqueId);
}

// General function to send data to Flask backend
function sendToFlask(endpoint, data) {
  fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((data) => console.log(data))
    .catch((error) => console.error("Error:", error));
}

// Utils
function get(selector, root = document) {
  return root.querySelector(selector);
}

function formatDate(date) {
  const h = "0" + date.getHours();
  const m = "0" + date.getMinutes();

  return `${h.slice(-2)}:${m.slice(-2)}`;
}

function generateUniqueId() {
  return `uniqueId_${++uniqueIdCounter}`;
}

function startAnimation() {
  blobs.classList.add("animate");
  blobs.classList.add("blobactive");
}

function stopAnimation() {
  blobs.classList.remove("animate");
  blobs.classList.remove("blobactive");
}

let stream = null;


async function toggleRecording() {
  const fast = fastBtn.checked || false;
  const slow = slowBtn.checked || false;
  const groq = groqBtn.checked || false;
  if (audio) {
    audio.pause();
  }
  playSoundEffect(voiceSound);
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    stopAnimation();
    
    playSoundEffect(msgsound);
    setTimeout(() => {
      appendMessage(transUser, PERSON_IMG, "right", `${svg}`);
    }, 700);

    setTimeout(() => {
      appendMessage(transJobBot, BOT_IMG, "left", loading);
    }, 1500);

    mediaRecorder.addEventListener("stop", () => {
      getLevelResponse(
        "level1",
        "",
        fast,
        slow,
        groq,
        "english"
      );
      // getLevelResponse("level1", "this is a test query", fast, "english");
      // getLevelResponse("level1", query, fast, leng);
      
      
      const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
      const audioUrl = URL.createObjectURL(audioBlob);

      // Stop each track in the stream
     
    });
  } else {
    if (stream) {
      stopMediaStream(); // Ensure any existing stream is stopped
  }
    if (!stream) { // Only get the user media if stream is not already present
      try {
        
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        
        mediaRecorder.addEventListener("dataavailable", (event) => {
          audioChunks.push(event.data);
        });
      
      } catch (error) {
        console.error("Error accessing the microphone:", error);
      }
    }
    if (mediaRecorder) {
      
      mediaRecorder.start();
      startAnimation();
    }
  }
}
function stopMediaStream() {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null; // Clear the stream
    playSoundEffect(msgsound); // Play a sound effect if needed
  }
}




function getLevelResponse(
  level,
  query,
  fast,
  slow,
  groq,
  leng = "",
  response = ""
) {
  console.log(level,'level in getLevel')
  const formData = new FormData();
  formData.append("query", query);
  formData.append("fast", fast);
  formData.append("leng", leng);
  formData.append("slow", slow);
  formData.append("groq", groq);
  formData.append("response", response);

  if (audioChunks.length > 0) {
    const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
    formData.append("audio", audioBlob);
    audioChunks = [];
  }

  fetch("/" + level, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      const streamEventSource = new EventSource("/" + level + "/stream");

      streamEventSource.onmessage = function (event) {
        const streamData = JSON.parse(event.data);


        if (streamData.endOfStream) {
          try {
            currentAns =  extractMessage(streamData.response)
            console.log(currentAns,'currentAns');
          } catch (err) {
            currentAns =  streamData.response
            console.log(err)
          }
          streamEventSource.close();
          iscompleted = true;

          currentQues = questionsList[0];

          if (questionFlag) {
            questionsAndAnswers.push({
              question: currentQues,
              answer: currentAns,
            });
          }

          questionsList.splice(0, 1);

          if (questionsList.length) {
            questionFlag = true;
            setTimeout(() => {
              askQuestion();
            }, 500);
          } else {
            questionFlag = false;
          }
        }
        // msgerChat.insertAdjacentHTML("beforeend", msgHTML);
        // msgerChat.scrollTop = msgerChat.scrollHeight;
        updateBox(level, streamData, query, fast);
      };

      streamEventSource.onerror = function (error) {
        console.error("EventSource failed:", error);
        streamEventSource.close();

        currentQues = questionsList[0];

        if (questionFlag) {
          questionsAndAnswers.push({
            question: currentQues,
            answer: currentAns,
          });
        }

        questionsList.splice(0, 1);

        if (questionsList.length) {
          setTimeout(() => {
            questionFlag = true;
            iscompleted = true;
            askQuestion();
          }, 500);
        } else {
          questionFlag = false;
        }
      };
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

function replaceWithNumbers(text) {
  let count = 0;
  return text.replace(/\[(.*?)\]/g, function (match, group) {
    count++;
    return `[<span class="tooltip" data-tooltip="${group}">${count}</span>]`;
  });
}

let l1Response = "";
let l2Response = "";
let l3Response = "";
let l2ResponseClicked = false;
let l3ResponseClicked = false;
let count = 0;

function updateMessageWithCitations(message, citations) {
  let updatedMessage = message.replace(/\[(\d+)\]/g, (match, index) => {
    let citationIndex = parseInt(index);
    if (citations[citationIndex]) {
      return `<a target='_blank' href="${citations[citationIndex]}">${match}</a>`;
    } else {
      return match; // If citation link doesn't exist, keep original text
    }
  });
  return updatedMessage;
}

function updateBox(level, data, query, fast, leng = "") {
  const chatext = document.querySelector(
    `[data-id=uniqueId_${uniqueIdCounter}]`
  );
  // if the data has end of flag , citation ? real expression

  let processedResponse = data.response;
  if (data.endOfStream) {
    let citationsRegex = /list_of_citations\s*=\s*(\[.*?\])/s; // Regex to match list_of_citations array
    let matchCitations = processedResponse.match(citationsRegex);
    let extractedCitations = matchCitations ? matchCitations[1] : ""; // Extracted list of citations

    let replacecc = "list_of_citations =";

    if (extractedCitations) {
      processedResponse = processedResponse.replace(
        `${extractedCitations}`,
        ""
      );
      processedResponse = processedResponse.replace(`${replacecc}`, "");

      processedResponse = updateMessageWithCitations(
        processedResponse,
        JSON.parse(extractedCitations)
      );
    }
  }


  processedResponse = processedResponse.replace(/\n/g, "<br>");

  chatext.innerHTML = `<div><p>${processedResponse}</p></div>`;
  msgerChat.scrollTop = msgerChat.scrollHeight;

  function appendButton(levelToShow, response, query, fast, slow, groq, leng) {
    const buttonId = `showLevel${levelToShow + count}ResponseBtn`;
    const responseDivId = `level${levelToShow + count}Response`;
    count = count + 2;
    msgerChat.scrollTop = msgerChat.scrollHeight;

    chatext.insertAdjacentHTML(
      "beforeend",
      `<div id="${responseDivId}" style="display:none;"><p>${response}</p></div><button id="${buttonId}" class="next-level-btn">${transBtn}</button>`
    );
    msgerChat.scrollTop = msgerChat.scrollHeight;

    document.getElementById(buttonId).addEventListener("click", function () {
      const responseDiv = document.getElementById(responseDivId);
      responseDiv.style.display = "block"; // Show the response
      this.style.display = "none"; // Hide the button
      msgerChat.scrollTop = msgerChat.scrollHeight;

      if (levelToShow === 2) {
        l2ResponseClicked = true;
        getLevelResponse("level2", query, fast, slow, groq, leng, response);
      } else if (levelToShow === 3) {
        l3ResponseClicked = true;
        getLevelResponse("level3", query, fast, slow, groq, leng, response);
      }
    });
  }

  if (data.endOfStream) {
    if (level === "level1") {
      appendButton(2, processedResponse, query, fast, slow, groq, leng);
    } else if (level === "level2") {
      appendButton(3, processedResponse, query, fast, slow, groq, leng);
    }
  }
}

queryInput.addEventListener("submit", function (event) {
  event.preventDefault();

  const query = document.getElementsByName("query")[0].value;
  if (query == "") {
    return alert("Please Enter something to Chat");
  }
  const fast = fastBtn.checked || false;
  const slow = slowBtn.checked || false;
  const groq = groqBtn.checked || false;
  playSoundEffect(submitFeedback);

  handleSubmitButton(query, fast, slow, groq);
});

function handleSubmitButton(
  query,
  fast,
  slow,
  groq,
  leng = "",
  level = "level1"
) {
  history.pushState({}, "", `/chat?q=${encodeURIComponent(query)}`);

  // isPlay = false;
  if (audio) {
    audio.pause();
  }

  if (audioChunks.length) {
    appendMessage(transUser, PERSON_IMG, "right", `${svg}`);
    // playSoundEffect(standardSound)
    audioChunks = [];
  } else {
    playSoundEffect(msgsound);
    appendMessage(transUser, PERSON_IMG, "right", query);
  }

  queryInput.disabled = true;
  setTimeout(() => {
    playSoundEffect(msgsound);
    appendMessage(transJobBot, BOT_IMG, "left", loading);
  }, 1000);
  console.log('qery form getlef',query)
  getLevelResponse(level, query, fast, slow, groq, leng);
  msgerInput.value = "";
}

function getSVG() {
  return `
   <div class='svgImg'>
   <svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg"  xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
	 width="100%" viewBox="0 0 1108 324" enable-background="new 0 0 1108 324" xml:space="preserve">
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M566.750000,89.500000 
	C567.944153,90.656303 567.484924,92.141533 567.485413,93.500008 
	C567.502869,141.500000 567.502502,189.500000 567.478943,237.499985 
	C567.478516,238.333099 567.928833,239.319092 567.000000,240.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M50.750000,89.500000 
	C51.944176,90.656303 51.484901,92.141533 51.485394,93.500008 
	C51.502861,141.500000 51.502544,189.500000 51.478992,237.499985 
	C51.478584,238.333099 51.928810,239.319092 51.000000,240.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M910.750000,89.500000 
	C911.944153,90.656303 911.484924,92.141533 911.485413,93.500008 
	C911.502869,141.500000 911.502502,189.500000 911.478943,237.499985 
	C911.478516,238.333099 911.928833,239.319092 911.000000,240.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M116.000000,90.000000 
	C114.956200,90.853813 115.531387,92.012909 115.530663,93.000023 
	C115.495605,141.000000 115.495605,189.000000 115.530663,236.999985 
	C115.531380,237.987091 114.956200,239.146194 116.000000,240.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M331.000000,90.000000 
	C330.833344,91.833336 330.522156,93.666580 330.521118,95.500015 
	C330.494263,141.833328 330.494263,188.166672 330.521088,234.499985 
	C330.522156,236.333405 330.833374,238.166672 331.000031,240.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M503.000000,90.000000 
	C501.956207,90.853813 502.531403,92.012909 502.530670,93.000023 
	C502.495636,141.000000 502.495636,189.000000 502.530701,236.999985 
	C502.531433,237.987091 501.956207,239.146194 503.000000,240.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M804.000000,90.000000 
	C802.956177,90.853813 803.531372,92.012909 803.530640,93.000023 
	C803.495605,141.000000 803.495605,189.000000 803.530640,236.999985 
	C803.531372,237.987091 802.956177,239.146194 804.000000,240.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M1040.000000,99.000000 
	C1041.043823,99.853813 1040.468506,101.012878 1040.469360,102.000023 
	C1040.505127,144.000000 1040.505127,186.000000 1040.469360,227.999969 
	C1040.468506,228.987122 1041.043823,230.146194 1040.000000,231.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M201.500000,99.500000 
	C201.500000,143.166672 201.500000,186.833328 201.500000,230.500000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M674.500000,99.500000 
	C674.500000,102.000000 674.500000,104.500000 674.500000,107.000000 
	C674.500000,145.666672 674.500000,184.333328 674.500000,223.000000 
	C674.500000,225.500000 674.500000,228.000000 674.500000,230.500000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M309.500000,100.500000 
	C309.500000,103.000000 309.500000,105.500000 309.500000,108.000000 
	C309.500000,146.000000 309.500000,184.000000 309.500000,222.000000 
	C309.500000,224.500000 309.500000,227.000000 309.500000,229.500000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M782.500000,100.500000 
	C782.500000,103.166664 782.500000,105.833336 782.500000,108.500000 
	C782.500000,139.833328 782.531860,171.166733 782.477112,202.499954 
	C782.463745,210.166901 782.166687,217.833328 782.000000,225.500000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M610.500000,104.500000 
	C610.500000,144.833328 610.500000,185.166672 610.500000,225.500000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M524.000000,111.500000 
	C524.824341,147.166672 524.824341,182.833328 524.000000,218.500000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M352.000000,111.500000 
	C352.824371,147.166672 352.824371,182.833328 352.000000,218.500000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M136.750000,115.500000 
	C137.827286,116.489395 137.493484,117.790237 137.493790,119.000000 
	C137.501648,150.000000 137.501938,181.000000 137.487396,212.000000 
	C137.487076,212.683212 137.822006,213.497162 137.000000,214.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M265.750000,115.500000 
	C266.827271,116.489395 266.493500,117.790237 266.493805,119.000000 
	C266.501648,150.000000 266.501923,181.000000 266.487396,212.000000 
	C266.487061,212.683212 266.821991,213.497162 266.000000,214.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M73.000000,116.000000 
	C71.956200,116.853813 72.532120,118.012802 72.530899,119.000038 
	C72.493141,149.666656 72.493141,180.333344 72.530899,210.999969 
	C72.532120,211.987198 71.956200,213.146194 73.000000,214.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M459.500000,121.500000 
	C459.500000,139.333328 459.500000,157.166672 459.500000,175.000000 
	C459.500000,186.166672 459.500000,197.333328 459.500000,208.500000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M825.500000,121.500000 
	C825.500000,138.833328 825.500000,156.166672 825.500000,173.500000 
	C825.500000,185.166672 825.500000,196.833328 825.500000,208.500000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M997.500000,121.500000 
	C997.500000,138.833328 997.500000,156.166672 997.500000,173.500000 
	C997.500000,185.166672 997.500000,196.833328 997.500000,208.500000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M223.000000,129.000000 
	C224.074142,130.037033 223.463531,131.347061 223.465988,132.500076 
	C223.512238,154.166641 223.512207,175.833359 223.465973,197.499924 
	C223.463501,198.652939 224.074142,199.962967 223.000000,201.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M395.000000,129.000000 
	C396.074158,130.037033 395.463531,131.347061 395.466003,132.500076 
	C395.512238,154.166641 395.512238,175.833359 395.466003,197.499924 
	C395.463531,198.652939 396.074158,199.962967 395.000000,201.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M1062.000000,134.000000 
	C1060.843994,137.621689 1061.568359,141.338577 1061.543579,145.000290 
	C1061.440063,160.332916 1061.475342,175.666763 1061.535522,190.999863 
	C1061.541992,192.657227 1060.941284,194.422531 1062.000000,196.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M933.000000,134.000000 
	C931.843994,137.621689 932.568420,141.338577 932.543701,145.000290 
	C932.440063,160.332916 932.475281,175.666763 932.535522,190.999863 
	C932.542053,192.657227 931.941284,194.422531 933.000000,196.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M739.000000,134.000000 
	C740.156006,137.621689 739.431519,141.338577 739.456299,145.000290 
	C739.559937,160.332916 739.524719,175.666763 739.464478,190.999863 
	C739.458008,192.657227 740.058716,194.422531 739.000000,196.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M632.000000,134.000000 
	C630.843994,137.621689 631.568420,141.338577 631.543701,145.000290 
	C631.440063,160.332916 631.475281,175.666763 631.535522,190.999863 
	C631.541992,192.657227 630.941284,194.422531 632.000000,196.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M546.000000,134.000000 
	C544.843994,137.621689 545.568420,141.338577 545.543701,145.000290 
	C545.440063,160.332916 545.475281,175.666763 545.535522,190.999863 
	C545.541992,192.657227 544.941284,194.422531 546.000000,196.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M868.000000,134.000000 
	C869.156006,137.621689 868.431580,141.338577 868.456299,145.000290 
	C868.559937,160.332916 868.524719,175.666763 868.464478,190.999863 
	C868.458008,192.657227 869.058716,194.422531 868.000000,196.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M288.000000,141.000000 
	C286.879578,150.984100 287.630981,161.001129 287.564545,171.000427 
	C287.524689,176.994064 286.853546,183.027222 288.000000,189.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M30.000000,144.000000 
	C29.166874,158.000000 29.166874,172.000000 30.000000,186.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M180.000000,144.000000 
	C180.833130,158.000000 180.833130,172.000000 180.000000,186.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M245.000000,144.000000 
	C244.166870,158.000000 244.166870,172.000000 245.000000,186.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M374.000000,144.000000 
	C373.166870,158.000000 373.166870,172.000000 374.000000,186.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M481.000000,144.000000 
	C481.833130,158.000000 481.833130,172.000000 481.000000,186.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M438.500000,148.500000 
	C438.500000,159.500000 438.500000,170.500000 438.500000,181.500000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M588.500000,148.500000 
	C588.500000,159.500000 588.500000,170.500000 588.500000,181.500000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M695.750000,148.500000 
	C697.330750,151.041901 696.480164,153.851669 696.433350,156.498825 
	C696.288818,164.665451 697.161255,172.853638 696.000000,181.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M93.750000,148.500000 
	C95.330765,151.041901 94.480141,153.851669 94.433304,156.498825 
	C94.288795,164.665451 95.161278,172.853638 94.000000,181.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M159.000000,149.000000 
	C158.175720,159.666672 158.175720,170.333328 159.000000,181.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M847.000000,149.000000 
	C846.175720,159.666672 846.175720,170.333328 847.000000,181.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M890.000000,149.000000 
	C889.175720,159.666672 889.175720,170.333328 890.000000,181.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M1019.000000,149.000000 
	C1018.175720,159.666672 1018.175720,170.333328 1019.000000,181.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M1083.000000,149.000000 
	C1083.824341,159.666672 1083.824341,170.333328 1083.000000,181.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M417.000000,152.000000 
	C416.178925,160.666672 416.178925,169.333328 417.000000,178.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M761.000000,152.000000 
	C760.178894,160.666672 760.178894,169.333328 761.000000,178.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M954.000000,152.000000 
	C954.821106,160.666672 954.821106,169.333328 954.000000,178.000000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M653.500000,153.500000 
	C653.500000,161.166672 653.500000,168.833328 653.500000,176.500000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M717.500000,153.500000 
	C717.500000,161.166672 717.500000,168.833328 717.500000,176.500000 
"/>
<path fill="none" opacity="1.000000" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="8.000000"
	d="
M975.500000,153.500000 
	C975.500000,161.166672 975.500000,168.833328 975.500000,176.500000 
"/>
</svg>
   </div>`;
}

function getloadingSvg() {
  return `<svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 200 40"
      width="150"
      height="30"
      fill="#3498db"
    >
      <circle cx="10" cy="20" r="4" class="dot dot1"></circle>
      <circle cx="30" cy="20" r="4" class="dot dot2"></circle>
      <circle cx="50" cy="20" r="4" class="dot dot3"></circle>
      <circle cx="70" cy="20" r="4" class="dot dot4"></circle>
      <circle cx="90" cy="20" r="4" class="dot dot5"></circle>
      <circle cx="110" cy="20" r="4" class="dot dot6"></circle>
      <circle cx="130" cy="20" r="4" class="dot dot7"></circle>
    </svg>`;
}

var arr = [...buttons];

arr.forEach((element, index) => {
  element.addEventListener("click", () => {
    arr.forEach((item) => {
      item.style.opacity = "0";
    });
    fastText.innerText = element.id;
    if (element.id == "slow") {
      let innerHTML = `<img class='textImg' src="/static/icons/gptSlow.svg" alt="slowGPT"  />`;
      fastText.innerHTML = innerHTML;
    } else if (element.id == "fast") {
      fastText.innerHTML = fastImg;
    } else if (element.id == "groq") {
      let groqImg = `<img class='textImg' src="/static/icons/groq.svg" alt="groq"  />`;
      fastText.innerHTML = groqImg;
    }
    playSoundEffect(toggle);
    element.style.opacity = "1";
  });
});

function playSoundEffect(audioUrl) {
  var audio = new Audio(audioUrl);
  audio.play();
}

const ctrPanelBtn = document.querySelector(".ctrPanelBtn");

ctrPanelBtn.addEventListener("click", moveToControlPanel);

function moveToControlPanel(e) {
  e.preventDefault();
  playSoundEffect(standardSound);
  setTimeout(() => {
    // alert('You will redireted be to Control Panel')
    window.location.href = "/control_panel";
  }, 500);
}

// modal ---------------------------------
const modalButton = document.querySelector(".chatList");
const modalBox = document.querySelector(".modalBox");
const modalClose = document.querySelector(".modalClose");
const modalContent = document.querySelector(".modal");

modalButton.addEventListener("click", (e) => {
  e.preventDefault();
  modalBox.style.width = "20%";
});

modalClose.addEventListener("click", (e) => {
  e.preventDefault();
  modalBox.style.width = "0%";
});

const modaldata = [
  { title: "What is FE?", id: "234sdf33423" },
  { title: "What is back end?", id: "234sdf3as3423" },
  { title: "What is this book about?", id: "23s4sdf33423" },
  { title: "What is sam?", id: "234sdf332423" },
];

const chats = [
  {
    bot: "Welcome to the alpha version of JobBot, created by Capria.",
    user: "What is genAIasf?",
  },
  {
    bot: "Welcome to the alpha version of JobBot, created by Capria.",
    user: "What is geaafenAI?",
  },
  {
    bot: "Welcome to the alpha version of JobBot, created by Capria.",
    user: "What is ge234234nAI?",
  },
];

function appendMessages(chats) {
  const container = document.getElementsByClassName("msger-chat")[0];

  container.innerHTML = "";

  chats.forEach((chat) => {
    if (chat.bot) {
      appendMessage(BOT_NAME, BOT_IMG, "left", chat?.bot);
    }
    if (chat.user) {
      appendMessage(PERSON_NAME, PERSON_IMG, "right", chat?.user);
    }
  });
}

function setChat(id) {
  appendMessages(chats);
}

function appendModalData(data) {
  modalContent.innerHTML = data
    .map((item) => {
      return (
        '<div class="conversationList">' +
        "<h5 onclick=\"setChat('" +
        item.id +
        "')\">" +
        item.title +
        "</h5>" +
        "</div>"
      );
    })
    .join(""); // Join the array of HTML strings into a single string
}

appendModalData(modaldata);

function playReceivedAudio(url) {
  if (audio) {
    audio.pause();

    audio.addEventListener("ended", function () {
      audio = null;
      isPlay = false;
    });
  }

  audio = new Audio();
  audio.src = url; // Set audio source
  if (isPlay) {
    audio.play(); // Play the audio
  }
}

function fetchData() {
  fetch("/audioInterval")
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.blob(); // Fetch audio file as blob
    })
    .then((blob) => {
      const audioURL = URL.createObjectURL(blob);
      if (blob.size) {
        isPlay = true;
        playReceivedAudio(audioURL);
      }
    })
    .catch((error) => {
      console.error("There was a problem with the fetch operation:", error);
    });
}

function fetchDataAfterTwoSec() {
  setInterval(fetchData, 100); // Call fetchData every 100ms
}

// fetchDataAfterTwoSec();

let isSpaceDown = false;
let startTime;
let endTime;
let startRecordingTimeout;

function startRecording() {
  toggleRecording();
}

function stopRecording() {
  toggleRecording();
}

document.addEventListener("keydown", (event) => {
  if (
    (event.code === "ShiftLeft" || event.code === "ShiftRight") &&
    !event.repeat
  ) {
    startRecordingTimeout = setTimeout(() => {
      isSpaceDown = true;

      startRecording();
    }, 1000);
  }
});

document.addEventListener("keyup", (event) => {
  if (event.code === "ShiftLeft" || event.code === "ShiftRight") {
    clearTimeout(startRecordingTimeout);
    if (isSpaceDown) {
      stopRecording();
    }
    isSpaceDown = false;
  }
});

let isMuted = false;

document.getElementById("muteButton").addEventListener("click", () => {
  isMuted = !isMuted; // Toggle the mute state

  if (isMuted) {
    audio.muted = true; // Mute the audio
    document.getElementById("muteButton").innerText = "Unmute";
  } else {
    audio.muted = false; // Unmute the audio
    document.getElementById("muteButton").innerText = "Mute";
  }
});

const stopBtn = document.getElementById("stopButton");

stopBtn.addEventListener("click", async () => {
  try {
    const isButtonOn = stopBtn.disabled;
    const response = await fetch("/stop", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ flag: !isButtonOn }), // Toggle the flag value
    });
    if (response.ok) {
    } else {
      console.error("Failed to send request to /stop:", response.statusText);
    }
  } catch (error) {
    console.error("Error sending request to /stop:", error);
  }
});

// upload question

const downloadBtn = document.getElementById("downloadBtn");

function handleUpload() {
  questionsAndAnswers = [];
  questionsList = [];
  questionFlag = true;
  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];
  iscompleted = true;
  if (file) {
    const reader = new FileReader();
    reader.onload = function (event) {
      const arrayBuffer = event.target.result;
      mammoth
        .extractRawText({ arrayBuffer: arrayBuffer })
        .then(function (result) {
          const text = result.value;
          const questions = extractQuestions(text);
          questionsList = questions;
          console.log("QUESTIONSSSSSSSSSSSSSSSSSSSSSSSSSSSSS", questionsList)
          askQuestion(questions);

          let button = document.createElement("button");
          button.innerText = "Download";

          const downloadBtn = document.getElementById("downloadBtn");
          downloadBtn.innerHTML = "";
          downloadBtn.appendChild(button);

          button.addEventListener("click", generateWordDocument);
        })
        .catch(function (err) {
          console.error("Error extracting text from DOCX:", err);
        });
    };
    reader.readAsArrayBuffer(file);
  }
}

function extractQuestions(text) {
  const lines = text.split("\n");
  const questions = [];
  let currentQuestion = "";

  for (const line of lines) {
    if (line.trim() === "") {
      if (currentQuestion !== "") {
        questions.push(currentQuestion.trim());
        currentQuestion = "";
      }
    } else {
      currentQuestion += line + "\n";
    }
  }

  return questions;
}

function containsSlashAsterisk(inputString) {
  return inputString.includes('/*');
}

function askQuestion(questions = []) {
  if (iscompleted) {
    const fast = fastBtn.checked || false;
    const slow = slowBtn.checked || false;
    const groq = groqBtn.checked || false;

    responseReceived = null;

    while (questionsList.length > 0) {
      console.log("ASKINGGGGGGGGGGG QUESTIONS!!!!!")
      if (containsSlashAsterisk(questionsList[0])) {
        console.log("Yep", questionsList)
          questionsAndAnswers.push({
            question: questionsList[0],
            answer:'',
          });
          questionsList.splice(0, 1);
        console.log("Removed", questionsList)
        // Removes 1 element at index 0
      } else {
          break;
      }
  }
    

    let level = separateLevel(questionsList[0]);
    let question = questionsList[0].replace("(L1)", "").replace("(L2)", "");
    question = removeNumericPrefix(question)
    console.log(level,question,questionsList[0],'-------')

    handleSubmitButton(question, fast, slow, groq, "", level);
    iscompleted = false;
  }
}

function separateLevel(line) {
  if (line.includes("(L1)")) {
    return "level1";
  } else if (line.includes("(L2)")) {
    return "level2";
  } else {
    return "No level found";
  }
}

function generateWordDocument() {
  let docxContent = "";
  questionsAndAnswers.forEach((qa, index) => {
    docxContent += `\n\n${qa.question}\n\n${qa.answer}`;
  });

  const blob = new Blob([docxContent], {
    type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  });
  saveAs(blob, "questions_and_answers.txt");
}

function extractMessage(response) {
  let updatedMessage = "";
  let citationsRegex = /list_of_citations\s*=\s*(\[.*?\])/s; // Regex to match list_of_citations array
  let matchCitations = response.match(citationsRegex);
  let extractedCitations = matchCitations ? matchCitations[1] : ""; // Extracted list of citations

  let replacecc = "list_of_citations =";

  if (extractedCitations) {
    response = response.replace(`${extractedCitations}`, "");
    updatedMessage = response.replace(`${replacecc}`, "");
  }

  if (updatedMessage == '') {
    updatedMessage = response
  }

  return updatedMessage;
}

document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('stopStreamBtn').addEventListener('click', function() {
      this.classList.toggle('cross');
  });
});
