/*=========================================================
    OKAI ERP Assistant
    app.js (V2)
=========================================================*/


/*=========================================================
    DOM
=========================================================*/

const moduleList = document.getElementById("module-list");

const viewerContent = document.getElementById("viewer-content");

const viewerTitle = document.getElementById("viewer-title");

const viewerSubtitle = document.getElementById("viewer-subtitle");

const chatList = document.getElementById("chat-list");

const form = document.getElementById("chat-form");

const input = document.getElementById("question-input");

const sendButton = document.getElementById("send-button");

const searchBox = document.getElementById("knowledge-search");

const searchClearButton = document.getElementById("search-clear");

const errorBanner = document.getElementById("error-banner");

const suggestionButtons =
    document.querySelectorAll(".ai-chip");

const moduleCount =
    document.getElementById("module-count");

const assistantPanel =
    document.getElementById("assistant-panel");

const chatFab =
    document.getElementById("chat-fab");

const chatCloseButton =
    document.getElementById("chat-close");

const questionCountEl =
    document.getElementById("question-count");

const themeToggleButton =
    document.getElementById("theme-toggle");

const printButton =
    document.getElementById("print-btn");

const shortcutsButton =
    document.getElementById("shortcuts-btn");

const shortcutsPopover =
    document.getElementById("shortcuts-popover");

const shortcutsCloseButton =
    document.getElementById("shortcuts-close");

const MODULE_COLORS = ["m0", "m1", "m2", "m3", "m4", "m5"];

// .chat-list itself doesn't scroll — its parent .chat-panel does.
const chatPanel = chatList.closest(".chat-panel") || chatList.parentElement;


/*=========================================================
    GLOBAL STATE
=========================================================*/

const state = {

    modules:[],

    currentModule:null,

    currentTopic:null,

    currentQuestion:null

};


/*=========================================================
    SEARCH STATE

    fullTreeCache holds the complete topics+questions
    payload per module (moduleName -> topics[]) so the
    search box can filter/highlight instantly without
    refetching. toggleModule() also writes into this
    cache, so anything the user expands manually is
    reused too.
=========================================================*/

const fullTreeCache = {};

let treeReadyPromise = null;

let searchDebounce = null;


/*=========================================================
    API
=========================================================*/

const api={

    async get(url){

        const response=await fetch(url);

        if(!response.ok){

            throw new Error(await response.text());

        }

        return await response.json();

    },

    async post(url,data){

        const response=await fetch(

            url,

            {

                method:"POST",

                headers:{

                    "Content-Type":"application/json"

                },

                body:JSON.stringify(data)

            }

        );

        if(!response.ok){

            const err=await response.json();

            throw new Error(

                err.detail ||

                "Unknown Error"

            );

        }

        return await response.json();

    }

};


/*=========================================================
    UTILITIES
=========================================================*/

function showError(message){

    errorBanner.textContent=message;

    errorBanner.classList.remove("hidden");

    setTimeout(()=>{

        errorBanner.classList.add("hidden");

    },4000);

}


function clearViewer(){

    viewerTitle.textContent="Welcome to OKAI";

    viewerSubtitle.textContent=

        "Select any question from the Knowledge Tree.";

}


function escapeHtml(text){

    return String(text)

        .replace(/&/g,"&amp;")

        .replace(/</g,"&lt;")

        .replace(/>/g,"&gt;");

}


function textMatches(text, lowerQuery){

    return typeof text==="string" &&

        text.toLowerCase().includes(lowerQuery);

}


function highlightMatch(text, lowerQuery){

    const safe = escapeHtml(text);

    if(!lowerQuery){

        return safe;

    }

    const escapedQuery = lowerQuery.replace(

        /[.*+?^${}()|[\]\\]/g,

        "\\$&"

    );

    const regex = new RegExp(

        "(" + escapedQuery + ")",

        "ig"

    );

    return safe.replace(

        regex,

        '<mark class="search-hit">$1</mark>'

    );

}


function scrollChatToBottom(){

    // Immediate scroll for the common case
    chatPanel.scrollTop = chatPanel.scrollHeight;

    // Then again after the browser has fully painted the
    // new bubble (handles markdown content, images, etc.
    // that can change height a frame later)
    requestAnimationFrame(()=>{

        requestAnimationFrame(()=>{

            chatPanel.scrollTop = chatPanel.scrollHeight;

        });

    });

}


function loadingButton(isLoading){

    sendButton.disabled=isLoading;

    input.disabled=isLoading;

    sendButton.textContent=

        isLoading

        ? "Thinking..."

        : "Send";

}


/*=========================================================
    INITIALIZATION
=========================================================*/

window.addEventListener(

    "DOMContentLoaded",

    ()=>{

        console.log(

            "OKAI Ready"

        );

        initTheme();

        showWelcome();

        loadModules();

    }

);
/*=========================================================
    CHAT FUNCTIONS
=========================================================*/

function appendUserMessage(message){

    const wrapper = document.createElement("div");

    wrapper.className = "chat-message user";

    wrapper.innerHTML = `

        <div class="chat-bubble">

            ${message}

        </div>

    `;

    chatList.appendChild(wrapper);

    scrollChatToBottom();

}


function appendAssistantMessage(message){

    const wrapper = document.createElement("div");

    wrapper.className = "chat-message assistant";

    wrapper.innerHTML = `

        <div class="chat-bubble">

            ${marked.parse(message)}

        </div>

    `;

    chatList.appendChild(wrapper);

    scrollChatToBottom();

}


/*=========================================================
    TYPING INDICATOR
=========================================================*/

function showTyping(){

    const wrapper = document.createElement("div");

    wrapper.className =

        "chat-message assistant";

    wrapper.id = "typing-indicator";

    wrapper.innerHTML = `

        <div class="chat-bubble">

            <div class="typing">

                <span></span>

                <span></span>

                <span></span>

            </div>

        </div>

    `;

    chatList.appendChild(wrapper);

    scrollChatToBottom();

}


function hideTyping(){

    const typing =

        document.getElementById(

            "typing-indicator"

        );

    if(typing){

        typing.remove();

        scrollChatToBottom();

    }

}


/*=========================================================
    ASK QUESTION
=========================================================*/

async function askQuestion(question){

    question = question.trim();

    if(question===""){

        showError(

            "Please enter a question."

        );

        return;

    }

    openChatWidget();

    appendUserMessage(question);

    input.value = "";

    loadingButton(true);

    showTyping();
    showViewerLoading();

    try{

        const result = await api.post(

            "/api/ask",

            {

                question

            }

        );

        hideTyping();

        appendAssistantMessage(

            result.answer

        );
        showKnowledge(
            result.knowledge
        );

    }

    catch(error){

        hideTyping();

        appendAssistantMessage(

            "❌ Unable to get response."

        );

        showError(

            error.message

        );

    }

    finally{

        loadingButton(false);

    }

}


/*=========================================================
    CHAT EVENTS
=========================================================*/

form.addEventListener(

    "submit",

    function(event){

        event.preventDefault();

        askQuestion(

            input.value

        );

    }

);


suggestionButtons.forEach(button=>{

    button.addEventListener(

        "click",

        ()=>{

            openChatWidget();

            askQuestion(

                button.dataset.question

            );

        }

    );

});


/*=========================================================
    CHAT WIDGET TOGGLE (floating button + panel)
=========================================================*/

function openChatWidget(){

    assistantPanel.classList.add("open");

    document.body.classList.add("chat-open");

    chatFab.classList.add("hidden");

    chatFab.setAttribute("aria-expanded", "true");

    // Give the open animation a beat, then focus the input
    setTimeout(()=>{

        input.focus();
        scrollChatToBottom();

    }, 200);

}


function closeChatWidget(){

    assistantPanel.classList.remove("open");

    document.body.classList.remove("chat-open");

    chatFab.classList.remove("hidden");

    chatFab.setAttribute("aria-expanded", "false");

}


function toggleChatWidget(){

    if(assistantPanel.classList.contains("open")){

        closeChatWidget();

    }

    else{

        openChatWidget();

    }

}


chatFab.addEventListener("click", toggleChatWidget);

chatCloseButton.addEventListener("click", closeChatWidget);

document.addEventListener("keydown", (event)=>{

    if(event.key === "Escape"){

        if(!shortcutsPopover.classList.contains("hidden")){
            closeShortcuts();
        }

        if(assistantPanel.classList.contains("open")){
            closeChatWidget();
        }

    }

});


/*=========================================================
    THEME (LIGHT / DARK)
=========================================================*/

function applyTheme(theme){

    document.documentElement.dataset.theme = theme;

    try{
        localStorage.setItem("okai-theme", theme);
    }
    catch(error){ /* storage unavailable, ignore */ }

}


function initTheme(){

    let saved = null;

    try{
        saved = localStorage.getItem("okai-theme");
    }
    catch(error){ /* storage unavailable, ignore */ }

    if(saved === "dark" || saved === "light"){
        applyTheme(saved);
        return;
    }

    const prefersDark =
        window.matchMedia &&
        window.matchMedia("(prefers-color-scheme: dark)").matches;

    applyTheme(prefersDark ? "dark" : "light");

}


function toggleTheme(){

    const current = document.documentElement.dataset.theme === "dark"
        ? "dark"
        : "light";

    applyTheme(current === "dark" ? "light" : "dark");

}


themeToggleButton.addEventListener("click", toggleTheme);


/*=========================================================
    PRINT
=========================================================*/

printButton.addEventListener("click", ()=>{

    window.print();

});


/*=========================================================
    KEYBOARD SHORTCUTS POPOVER
=========================================================*/

function openShortcuts(){

    shortcutsPopover.classList.remove("hidden");

    shortcutsButton.setAttribute("aria-expanded", "true");

}


function closeShortcuts(){

    shortcutsPopover.classList.add("hidden");

    shortcutsButton.setAttribute("aria-expanded", "false");

}


function toggleShortcuts(){

    if(shortcutsPopover.classList.contains("hidden")){
        openShortcuts();
    }
    else{
        closeShortcuts();
    }

}


shortcutsButton.addEventListener("click", toggleShortcuts);

shortcutsCloseButton.addEventListener("click", closeShortcuts);

document.addEventListener("click", (event)=>{

    if(shortcutsPopover.classList.contains("hidden")){
        return;
    }

    if(shortcutsPopover.contains(event.target) ||
        shortcutsButton.contains(event.target)){
        return;
    }

    closeShortcuts();

});


/*=========================================================
    GLOBAL KEYBOARD SHORTCUTS
    "/" focuses search, "d" toggles theme, "?" toggles
    the shortcuts popover — all skipped while the user
    is already typing in a field.
=========================================================*/

function isTypingTarget(target){

    const tag = target.tagName;

    return tag === "INPUT" ||
        tag === "TEXTAREA" ||
        target.isContentEditable;

}


document.addEventListener("keydown", (event)=>{

    if(isTypingTarget(event.target)){
        return;
    }

    if(event.key === "/"){

        event.preventDefault();
        searchBox.focus();

    }

    else if(event.key === "d" || event.key === "D"){

        toggleTheme();

    }

    else if(event.key === "?"){

        toggleShortcuts();

    }

});


/*=========================================================
    KNOWLEDGE VIEWER
=========================================================*/

function showWelcome(){

    viewerTitle.textContent = "Welcome to OKAI";

    viewerSubtitle.textContent =
        "Select a question from the Knowledge Tree or ask the AI Assistant.";

    viewerContent.innerHTML = `

        <div class="welcome-card">

            <h2>📖 OKAI Knowledge Center</h2>

            <p>

                Browse ERP documentation using the Knowledge Tree.

            </p>

            <p>

                Select a topic and question from the left panel.

            </p>

            <p>

                The complete ERP documentation will appear here.

            </p>

        </div>

    `;

}


/*=========================================================
    SHOW LOADING
=========================================================*/

function showViewerLoading(){

    viewerContent.innerHTML = `

        <div class="welcome-card">

            <h2>Searching Knowledge...</h2>

            <p>

                Retrieving documentation from the ERP knowledge base...

            </p>

        </div>

    `;

}


/*=========================================================
    NAVIGATION FLOWCHART

    Turns a topic's navigation[] array (e.g. ["Settings",
    "Fees", "Concessions"]) into a row of connected steps,
    instead of a plain bulleted list.
=========================================================*/

function renderNavigationFlowchart(steps){

    const stepsHtml = steps.map((step, index)=>{

        const box = `<span class="nav-flow-step">${escapeHtml(step)}</span>`;

        if(index === steps.length - 1){
            return box;
        }

        return box + `<span class="nav-flow-arrow" aria-hidden="true">&rarr;</span>`;

    }).join("");

    return `<div class="nav-flowchart">${stepsHtml}</div>`;

}


/*=========================================================
    SHOW KNOWLEDGE
=========================================================*/

function showKnowledge(items){

    if(!items || items.length===0){

        showWelcome();

        return;

    }

    const topic = items[0];

    viewerTitle.textContent = topic.topic;

    viewerSubtitle.textContent =
        topic.module;

    let html = `

    <div class="doc-card">

        <h2>${topic.topic}</h2>

    `;

    if(topic.summary){

        html += `

        <h3>Summary</h3>

        <p>

            ${topic.summary}

        </p>

        `;

    }

    if(topic.navigation &&
       topic.navigation.length){

        html += `

        <h3>Navigation</h3>

        ${renderNavigationFlowchart(topic.navigation)}

        `;

    }

    html += `

        <button class="ask-ai-btn" id="ask-ai-btn" type="button">
            💬 Ask the AI about this topic
        </button>

    </div>

    `;

    viewerContent.innerHTML = html;

    const askAiBtn = document.getElementById("ask-ai-btn");

    if(askAiBtn){

        askAiBtn.addEventListener("click", ()=>{
            openChatWidget();
            input.value = "Tell me more about: " + topic.topic;
            input.focus();
        });

    }

}
/*=========================================================
    KNOWLEDGE TREE
=========================================================*/

async function loadModules(){

    try{

        const modules = await api.get("/api/modules");

        state.modules = modules;

        moduleCount.textContent = modules.length;

        renderModules(modules);

        treeReadyPromise = prefetchFullTree(modules);

    }

    catch(error){

        showError(error.message);

    }

}


/*=========================================================
    PREFETCH FULL TREE (for search)

    Fetches topics+questions for every module in the
    background so the search box can filter instantly.
    Silent on failure per-module; search just treats an
    unfetchable module as having no matches.
=========================================================*/

async function prefetchFullTree(modules){

    await Promise.all(

        modules.map(async module=>{

            if(fullTreeCache[module.module]){
                updateQuestionCountStat();
                return;

            }

            try{

                const topics = await api.get(
                    "/api/module/" + encodeURIComponent(module.module)
                );

                fullTreeCache[module.module] = topics;

            }

            catch(error){

                fullTreeCache[module.module] = [];

            }

            updateQuestionCountStat();

        })

    );

}


function updateQuestionCountStat(){

    if(!questionCountEl){
        return;
    }

    let total = 0;

    Object.values(fullTreeCache).forEach(topics=>{

        (topics || []).forEach(topic=>{
            total += topic.question_count || 0;
        });

    });

    questionCountEl.textContent = total;

}


/*=========================================================
    RENDER MODULES
=========================================================*/

function renderModules(modules){

    moduleList.innerHTML="";

    const maxTopics = Math.max(1, ...modules.map(m=>m.topics || 0));

    modules.forEach((module, index)=>{

        const colorVar = MODULE_COLORS[index % MODULE_COLORS.length];

        const barPercent = Math.max(
            6,
            Math.round(((module.topics || 0) / maxTopics) * 100)
        );

        const item=document.createElement("div");

        item.className="tree-module";

        item.dataset.moduleName=module.module;

        item.style.setProperty(
            "--module-accent",
            `var(--${colorVar})`
        );

        item.innerHTML=`

            <div
                class="tree-module-header">

                <div
                    class="tree-module-left">

                    <span
                        class="tree-arrow">

                        ▶

                    </span>

                    <span
                        class="tree-icon">

                        📁

                    </span>

                    <span
                        class="tree-module-title">

                        ${module.module}

                    </span>

                </div>

                <span
                    class="tree-count">

                    ${module.topics}

                </span>

            </div>

            <div class="tree-bar">
                <div class="tree-bar-fill" style="width:${barPercent}%"></div>
            </div>

            <div
                class="tree-topics">

            </div>

        `;

        const header=

            item.querySelector(

                ".tree-module-header"

            );

        header.addEventListener(

            "click",

            ()=>{

                toggleModule(

                    item,

                    module.module

                );

            }

        );

        moduleList.appendChild(item);

    });

}
/*=========================================================
    MODULE
=========================================================*/

async function toggleModule(card, module) {

    // Close every other module
    document.querySelectorAll(".tree-module").forEach(m => {

        if (m !== card) {

            m.classList.remove("open");

            // Close all topics inside that module
            m.querySelectorAll(".tree-topic").forEach(t => {
                t.classList.remove("open");
            });

        }

    });

    // Toggle current module
    if (card.classList.contains("open")) {

        card.classList.remove("open");

        card.querySelectorAll(".tree-topic").forEach(t => {
            t.classList.remove("open");
        });

        return;

    }

    card.classList.add("open");

    const topicsBox = card.querySelector(".tree-topics");

    // Already loaded
    if (topicsBox.dataset.loaded === "true") {
        return;
    }

    topicsBox.innerHTML = `
        <div class="tree-empty">
            Loading...
        </div>
    `;

    try {

        let topics = fullTreeCache[module];

        if (!topics) {

            topics = await api.get(
                "/api/module/" + encodeURIComponent(module)
            );

            fullTreeCache[module] = topics;

        }

        renderTopics(topicsBox, topics);

        topicsBox.dataset.loaded = "true";

    } catch (error) {

        topicsBox.innerHTML = `
            <div class="tree-empty">
                Unable to load topics.
            </div>
        `;

    }

}
/*=========================================================
    TOPICS
=========================================================*/

function renderTopics(container,topics){

    container.innerHTML="";

    topics.forEach(topic=>{

        const div=

        document.createElement("div");

        div.className="tree-topic";

        div.innerHTML=`

            <div
                class="tree-topic-header">

                <div
                    class="tree-topic-left">

                    <span
                        class="tree-arrow">

                        ▶

                    </span>

                    <span>

                        📂

                    </span>

                    <span
                        class="tree-topic-title">

                        ${topic.topic}

                    </span>

                </div>

                <span
                    class="tree-count">

                    ${topic.question_count}

                </span>

            </div>

            <div
                class="tree-questions">

            </div>

        `;

        div

        .querySelector(

            ".tree-topic-header"

        )

        .addEventListener(

            "click",

            ()=>{

                toggleTopic(

                    div,

                    topic

                );

            }

        );

        container.appendChild(div);

    });

}
/*=========================================================
    QUESTIONS
=========================================================*/

function toggleTopic(card, topic) {

    const parent = card.parentElement;

    // Close other topics in this module
    parent.querySelectorAll(".tree-topic").forEach(t => {

        if (t !== card) {

            t.classList.remove("open");

        }

    });

    // Toggle current topic
    if (card.classList.contains("open")) {

        card.classList.remove("open");

        return;

    }

    card.classList.add("open");

    const questionBox = card.querySelector(".tree-questions");

    if (questionBox.childElementCount > 0) {
        return;
    }

    topic.questions.forEach(question => {

        const div = document.createElement("div");

        div.className = "tree-question";

        div.textContent = question;

        div.addEventListener("click", () => {

            document
                .querySelectorAll(".tree-question")
                .forEach(q => q.classList.remove("active"));

            div.classList.add("active");

            askQuestion(question);

        });

        questionBox.appendChild(div);

    });

}
/*=========================================================
    KNOWLEDGE TREE SEARCH

    Typing in the search box filters the whole tree:
    modules/topics that contain a match auto-expand,
    matching text is highlighted, and non-matching
    branches are hidden. Every visible question is the
    same clickable node used elsewhere, so clicking a
    highlighted result navigates in a single step.
=========================================================*/

function getModuleCard(moduleName){

    return moduleList.querySelector(

        `.tree-module[data-module-name="${CSS.escape(moduleName)}"]`

    );

}


function renderSearchTopics(container, topics, lowerQuery){

    container.innerHTML = "";

    let matchedAny = false;

    topics.forEach(topic=>{

        const topicMatches = textMatches(topic.topic, lowerQuery);

        const matchingQuestions = (topic.questions || [])
            .filter(q => textMatches(q, lowerQuery));

        if(!topicMatches && matchingQuestions.length === 0){

            return;

        }

        matchedAny = true;

        const div = document.createElement("div");

        div.className = "tree-topic open";

        div.innerHTML = `

            <div class="tree-topic-header">

                <div class="tree-topic-left">

                    <span class="tree-arrow">▶</span>

                    <span>📂</span>

                    <span class="tree-topic-title">${highlightMatch(topic.topic, lowerQuery)}</span>

                </div>

                <span class="tree-count">${topic.question_count}</span>

            </div>

            <div class="tree-questions open"></div>

        `;

        div.querySelector(".tree-topic-header")
            .addEventListener("click", ()=>{
                toggleTopic(div, topic);
            });

        const questionBox = div.querySelector(".tree-questions");

        const questionsToShow = topicMatches
            ? (topic.questions || [])
            : matchingQuestions;

        questionsToShow.forEach(question=>{

            const qDiv = document.createElement("div");

            qDiv.className = "tree-question";

            qDiv.innerHTML = highlightMatch(question, lowerQuery);

            qDiv.addEventListener("click", ()=>{

                document.querySelectorAll(".tree-question")
                    .forEach(q => q.classList.remove("active"));

                qDiv.classList.add("active");

                askQuestion(question);

            });

            questionBox.appendChild(qDiv);

        });

        container.appendChild(div);

    });

    if(!matchedAny){

        container.innerHTML = `
            <div class="tree-empty">
                No matching topics.
            </div>
        `;

    }

}


async function filterKnowledgeTree(rawQuery){

    const lowerQuery = rawQuery.trim().toLowerCase();

    searchClearButton.classList.toggle("hidden", lowerQuery === "");

    if(!lowerQuery){

        resetKnowledgeTree();

        return;

    }

    if(treeReadyPromise){

        try{ await treeReadyPromise; } catch(error){ /* ignore */ }

    }

    let anyModuleMatched = false;

    state.modules.forEach(module=>{

        const moduleCard = getModuleCard(module.module);

        if(!moduleCard){

            return;

        }

        const topics = fullTreeCache[module.module] || [];

        const moduleNameMatches = textMatches(module.module, lowerQuery);

        const hasDescendantMatch = topics.some(topic=>{

            return textMatches(topic.topic, lowerQuery) ||
                (topic.questions || []).some(q => textMatches(q, lowerQuery));

        });

        const titleEl = moduleCard.querySelector(".tree-module-title");

        if(!moduleNameMatches && !hasDescendantMatch){

            moduleCard.classList.add("search-no-match");

            titleEl.textContent = module.module;

            return;

        }

        anyModuleMatched = true;

        moduleCard.classList.remove("search-no-match");

        moduleCard.classList.add("open");

        titleEl.innerHTML = highlightMatch(
            module.module,
            moduleNameMatches ? lowerQuery : ""
        );

        const topicsBox = moduleCard.querySelector(".tree-topics");

        topicsBox.dataset.loaded = "true";

        renderSearchTopics(topicsBox, topics, lowerQuery);

    });

    let emptyNotice = moduleList.querySelector(".tree-search-empty");

    if(!anyModuleMatched){

        if(!emptyNotice){

            emptyNotice = document.createElement("div");

            emptyNotice.className = "tree-empty tree-search-empty";

            moduleList.appendChild(emptyNotice);

        }

        emptyNotice.textContent =
            `No results found for "${rawQuery.trim()}".`;

    }

    else if(emptyNotice){

        emptyNotice.remove();

    }

}


function resetKnowledgeTree(){

    const emptyNotice = moduleList.querySelector(".tree-search-empty");

    if(emptyNotice){

        emptyNotice.remove();

    }

    document.querySelectorAll(".tree-module").forEach(card=>{

        card.classList.remove("search-no-match", "open");

        const titleEl = card.querySelector(".tree-module-title");

        if(titleEl){

            titleEl.textContent = card.dataset.moduleName;

        }

        const topicsBox = card.querySelector(".tree-topics");

        if(topicsBox){

            topicsBox.innerHTML = "";

            delete topicsBox.dataset.loaded;

        }

    });

}


/*=========================================================
    SEARCH EVENTS
=========================================================*/

searchBox.addEventListener("input", ()=>{

    clearTimeout(searchDebounce);

    const value = searchBox.value;

    searchDebounce = setTimeout(()=>{

        filterKnowledgeTree(value);

    }, 200);

});


searchBox.addEventListener("keydown", (event)=>{

    if(event.key === "Escape"){

        searchBox.value = "";

        filterKnowledgeTree("");

    }

});


searchClearButton.addEventListener("click", ()=>{

    searchBox.value = "";

    filterKnowledgeTree("");

    searchBox.focus();

});