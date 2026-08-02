/*=========================================================
    OKAI ERP Assistant - Core Logic
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
const suggestionButtons = document.querySelectorAll(".ai-chip");
const moduleCount = document.getElementById("module-count");
const assistantPanel = document.getElementById("assistant-panel");
const chatFab = document.getElementById("chat-fab");
const chatCloseButton = document.getElementById("chat-close");
const questionCountEl = document.getElementById("question-count");
const themeToggleButton = document.getElementById("theme-toggle");
const printButton = document.getElementById("print-btn");
const shortcutsButton = document.getElementById("shortcuts-btn");
const shortcutsPopover = document.getElementById("shortcuts-popover");
const shortcutsCloseButton = document.getElementById("shortcuts-close");
const MODULE_COLORS = ["m0", "m1", "m2", "m3", "m4", "m5"];

const chatPanel = chatList.closest(".chat-panel") || chatList.parentElement;

const state = { modules:[], currentModule:null, currentTopic:null, currentQuestion:null };
const fullTreeCache = {};
let treeReadyPromise = null;
let searchDebounce = null;

const api={
    async get(url){
        const response=await fetch(url);
        if(!response.ok) throw new Error(await response.text());
        return await response.json();
    },
    async post(url,data){
        const response=await fetch(url, { method:"POST", headers:{ "Content-Type":"application/json" }, body:JSON.stringify(data) });
        if(!response.ok){
            const err=await response.json();
            throw new Error(err.detail || "Unknown Error");
        }
        return await response.json();
    }
};

function showError(message){
    errorBanner.textContent=message;
    errorBanner.classList.remove("hidden");
    setTimeout(()=>{ errorBanner.classList.add("hidden"); },4000);
}

function clearViewer(){
    viewerTitle.textContent="System Standby";
    viewerSubtitle.textContent="Select a node from the Knowledge Explorer.";
}

function escapeHtml(text){
    return String(text).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

function textMatches(text, lowerQuery){ return typeof text==="string" && text.toLowerCase().includes(lowerQuery); }

function highlightMatch(text, lowerQuery){
    const safe = escapeHtml(text);
    if(!lowerQuery) return safe;
    const escapedQuery = lowerQuery.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const regex = new RegExp("(" + escapedQuery + ")", "ig");
    return safe.replace(regex, '<mark class="search-hit">$1</mark>');
}

function scrollChatToBottom(){
    chatPanel.scrollTop = chatPanel.scrollHeight;
    requestAnimationFrame(()=>{
        requestAnimationFrame(()=>{ chatPanel.scrollTop = chatPanel.scrollHeight; });
    });
}



function loadingButton(isLoading){
    sendButton.disabled=isLoading;
    input.disabled=isLoading;
    sendButton.innerHTML= isLoading ? `<div class="typing" style="padding:0"><span></span><span></span><span></span></div>` : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M22 2L11 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
}

window.addEventListener("DOMContentLoaded", ()=>{
    console.log("OKAI Ready");
    initTheme();
    loadModules();
});

function appendUserMessage(message){
    const wrapper = document.createElement("div");
    wrapper.className = "chat-message user";
    wrapper.innerHTML = `<div class="chat-bubble">${message}</div>`;
    chatList.appendChild(wrapper);
    scrollChatToBottom();
}

function appendAssistantMessage(message){
    const wrapper = document.createElement("div");
    wrapper.className = "chat-message assistant";
    // Marked usage preserved exactly
    wrapper.innerHTML = `<div class="chat-bubble">${marked.parse(message)}</div>`;
    chatList.appendChild(wrapper);
    // Auto-highlight code blocks
    wrapper.querySelectorAll('pre code').forEach((block) => { hljs.highlightElement(block); });
    scrollChatToBottom();
}

function showTyping(){
    const wrapper = document.createElement("div");
    wrapper.className = "chat-message assistant";
    wrapper.id = "typing-indicator";
    wrapper.innerHTML = `<div class="chat-bubble"><div class="typing"><span></span><span></span><span></span></div></div>`;
    chatList.appendChild(wrapper);
    scrollChatToBottom();
}

function hideTyping(){
    const typing = document.getElementById("typing-indicator");
    if(typing){ typing.remove(); scrollChatToBottom(); }
}

async function askQuestion(question){
    question = question.trim();
    if(question===""){ showError("Please enter a question."); return; }
    openChatWidget();
    appendUserMessage(question);
    input.value = "";
    loadingButton(true);
    showTyping();
    showViewerLoading();
    try{
        const result = await api.post("/api/ask", { question });
        hideTyping();
        appendAssistantMessage(result.answer);
        showKnowledge(result.knowledge);
    } catch(error){
        hideTyping();
        appendAssistantMessage("❌ Unable to connect to neural net.");
        showError(error.message);
    } finally {
        loadingButton(false);
    }
}

form.addEventListener("submit", function(event){ event.preventDefault(); askQuestion(input.value); });

suggestionButtons.forEach(button=>{
    button.addEventListener("click", ()=>{ openChatWidget(); askQuestion(button.dataset.question); });
});

function openChatWidget(){
    assistantPanel.classList.add("open");
    document.body.classList.add("chat-open");
    chatFab.classList.add("hidden");
    chatFab.setAttribute("aria-expanded", "true");
    setTimeout(()=>{ input.focus(); scrollChatToBottom(); }, 200);
}

function closeChatWidget(){
    assistantPanel.classList.remove("open");
    document.body.classList.remove("chat-open");
    chatFab.classList.remove("hidden");
    chatFab.setAttribute("aria-expanded", "false");
}

function toggleChatWidget(){ assistantPanel.classList.contains("open") ? closeChatWidget() : openChatWidget(); }

chatFab.addEventListener("click", toggleChatWidget);
chatCloseButton.addEventListener("click", closeChatWidget);
document.addEventListener("keydown", (event)=>{
    if(event.key === "Escape"){
        if(!shortcutsPopover.classList.contains("hidden")) closeShortcuts();
        if(assistantPanel.classList.contains("open")) closeChatWidget();
    }
});

function applyTheme(theme){
    document.documentElement.dataset.theme = theme;
    try{ localStorage.setItem("okai-theme", theme); } catch(error){ }
}
function initTheme(){ applyTheme("dark"); } // Forced Dark Mode per requirements
function toggleTheme(){ const current = document.documentElement.dataset.theme; applyTheme(current === "dark" ? "light" : "dark"); }
themeToggleButton.addEventListener("click", toggleTheme);

printButton.addEventListener("click", ()=>{ window.print(); });

function openShortcuts(){ shortcutsPopover.classList.remove("hidden"); shortcutsButton.setAttribute("aria-expanded", "true"); }
function closeShortcuts(){ shortcutsPopover.classList.add("hidden"); shortcutsButton.setAttribute("aria-expanded", "false"); }
function toggleShortcuts(){ shortcutsPopover.classList.contains("hidden") ? openShortcuts() : closeShortcuts(); }

shortcutsButton.addEventListener("click", toggleShortcuts);
shortcutsCloseButton.addEventListener("click", closeShortcuts);
document.addEventListener("click", (event)=>{
    if(shortcutsPopover.classList.contains("hidden")) return;
    if(shortcutsPopover.contains(event.target) || shortcutsButton.contains(event.target)) return;
    closeShortcuts();
});

function isTypingTarget(target){ const tag = target.tagName; return tag === "INPUT" || tag === "TEXTAREA" || target.isContentEditable; }

document.addEventListener("keydown", (event)=>{
    if(isTypingTarget(event.target)) return;
    if(event.key === "/"){ event.preventDefault(); searchBox.focus(); }
    else if(event.key === "d" || event.key === "D"){ toggleTheme(); }
    else if(event.key === "?"){ toggleShortcuts(); }
});

function showViewerLoading(){
    viewerContent.innerHTML = `<div class="welcome-card glass-card"><h2><div class="typing" style="justify-content:center"><span></span><span></span><span></span></div></h2><p>Synthesizing documentation from enterprise nodes...</p></div>`;
}

function renderNavigationFlowchart(steps){
    const stepsHtml = steps.map((step, index)=>{
        const box = `<span class="nav-flow-step">${escapeHtml(step)}</span>`;
        if(index === steps.length - 1) return box;
        return box + `<span class="nav-flow-arrow" aria-hidden="true">&rarr;</span>`;
    }).join("");
    return `<div class="nav-flowchart">${stepsHtml}</div>`;
}

function showKnowledge(items){
    if(!items || items.length===0){ return; }
    const topic = items[0];
    viewerTitle.textContent = topic.topic;
    viewerSubtitle.textContent = topic.module;
    let html = `<div class="doc-card"><h2>${topic.topic}</h2>`;
    if(topic.summary) html += `<h3>Synthesis</h3><p>${topic.summary}</p>`;
    if(topic.navigation && topic.navigation.length) html += `<h3 class="nav-path-heading">System Path</h3>${renderNavigationFlowchart(topic.navigation)}`;
    html += `<button class="ask-ai-btn ripple" id="ask-ai-btn" type="button">✨ Probe neural net for deeper insight</button></div>`;
    viewerContent.innerHTML = html;
    const askAiBtn = document.getElementById("ask-ai-btn");
    if(askAiBtn){
        askAiBtn.addEventListener("click", ()=>{
            openChatWidget();
            input.value = "Expand on: " + topic.topic;
            input.focus();
        });
    }
    // Always bring the navigation/System Path section into view in the middle panel
    const navHeading = viewerContent.querySelector(".nav-path-heading");
    requestAnimationFrame(()=>{
        if(navHeading){
            navHeading.scrollIntoView({ behavior: "smooth", block: "start" });
        } else {
            viewerContent.scrollTop = 0;
        }
    });
}

async function loadModules(){
    try{
        const modules = await api.get("/api/modules");
        state.modules = modules;
        moduleCount.textContent = modules.length;
        renderModules(modules);
        treeReadyPromise = prefetchFullTree(modules);
    } catch(error){ showError(error.message); }
}

async function prefetchFullTree(modules){
    await Promise.all(
        modules.map(async module=>{
            if(fullTreeCache[module.module]){ updateQuestionCountStat(); return; }
            try{
                const topics = await api.get("/api/module/" + encodeURIComponent(module.module));
                fullTreeCache[module.module] = topics;
            } catch(error){ fullTreeCache[module.module] = []; }
            updateQuestionCountStat();
        })
    );
}

function updateQuestionCountStat(){
    if(!questionCountEl) return;
    let total = 0;
    Object.values(fullTreeCache).forEach(topics=>{ (topics || []).forEach(topic=>{ total += topic.question_count || 0; }); });
    questionCountEl.textContent = total;
}

function renderModules(modules){
    moduleList.innerHTML="";
    const maxTopics = Math.max(1, ...modules.map(m=>m.topics || 0));
    modules.forEach((module, index)=>{
        const colorVar = MODULE_COLORS[index % MODULE_COLORS.length];
        const barPercent = Math.max(6, Math.round(((module.topics || 0) / maxTopics) * 100));
        const item=document.createElement("div");
        item.className="tree-module";
        item.dataset.moduleName=module.module;
        item.style.setProperty("--module-accent", `var(--${colorVar})`);
        item.innerHTML=`
            <div class="tree-module-header">
                <div class="tree-module-left">
                    <span class="tree-arrow">▶</span>
                    <span class="tree-icon">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
                    </span>
                    <span class="tree-module-title">${module.module}</span>
                </div>
                <span class="tree-count">${module.topics}</span>
            </div>
            <div class="tree-bar"><div class="tree-bar-fill" style="width:${barPercent}%"></div></div>
            <div class="tree-topics"></div>
        `;
        item.querySelector(".tree-module-header").addEventListener("click", ()=>toggleModule(item, module.module));
        moduleList.appendChild(item);
    });
}

async function toggleModule(card, module) {
    document.querySelectorAll(".tree-module").forEach(m => {
        if (m !== card) { m.classList.remove("open"); m.querySelectorAll(".tree-topic").forEach(t => { t.classList.remove("open"); }); }
    });
    if (card.classList.contains("open")) {
        card.classList.remove("open");
        card.querySelectorAll(".tree-topic").forEach(t => { t.classList.remove("open"); });
        return;
    }
    card.classList.add("open");
    const topicsBox = card.querySelector(".tree-topics");
    if (topicsBox.dataset.loaded === "true") return;
    topicsBox.innerHTML = `<div class="tree-empty">Loading nodes...</div>`;
    try {
        let topics = fullTreeCache[module];
        if (!topics) { topics = await api.get("/api/module/" + encodeURIComponent(module)); fullTreeCache[module] = topics; }
        renderTopics(topicsBox, topics);
        topicsBox.dataset.loaded = "true";
    } catch (error) { topicsBox.innerHTML = `<div class="tree-empty">Node unavailable.</div>`; }
}

function renderTopics(container,topics){
    container.innerHTML="";
    topics.forEach(topic=>{
        const div=document.createElement("div"); div.className="tree-topic";
        div.innerHTML=`
            <div class="tree-topic-header">
                <div class="tree-topic-left">
                    <span class="tree-topic-title">${topic.topic}</span>
                </div>
                <span class="tree-count">${topic.question_count}</span>
            </div>
            <div class="tree-questions"></div>
        `;
        div.querySelector(".tree-topic-header").addEventListener("click", ()=>toggleTopic(div, topic));
        container.appendChild(div);
    });
}

function toggleTopic(card, topic) {
    const parent = card.parentElement;
    parent.querySelectorAll(".tree-topic").forEach(t => { if (t !== card) t.classList.remove("open"); });
    if (card.classList.contains("open")) { card.classList.remove("open"); return; }
    card.classList.add("open");
    const questionBox = card.querySelector(".tree-questions");
    if (questionBox.childElementCount > 0) return;
    topic.questions.forEach(question => {
        const div = document.createElement("div"); div.className = "tree-question"; div.textContent = question;
        div.addEventListener("click", () => {
            document.querySelectorAll(".tree-question").forEach(q => q.classList.remove("active"));
            div.classList.add("active");
            askQuestion(question);
        });
        questionBox.appendChild(div);
    });
}

function getModuleCard(moduleName){ return moduleList.querySelector(`.tree-module[data-module-name="${CSS.escape(moduleName)}"]`); }

function renderSearchTopics(container, topics, lowerQuery){
    container.innerHTML = "";
    let matchedAny = false;
    topics.forEach(topic=>{
        const topicMatches = textMatches(topic.topic, lowerQuery);
        const matchingQuestions = (topic.questions || []).filter(q => textMatches(q, lowerQuery));
        if(!topicMatches && matchingQuestions.length === 0) return;
        matchedAny = true;
        const div = document.createElement("div"); div.className = "tree-topic open";
        div.innerHTML = `
            <div class="tree-topic-header">
                <div class="tree-topic-left"><span class="tree-topic-title">${highlightMatch(topic.topic, lowerQuery)}</span></div>
                <span class="tree-count">${topic.question_count}</span>
            </div>
            <div class="tree-questions open"></div>
        `;
        div.querySelector(".tree-topic-header").addEventListener("click", ()=>toggleTopic(div, topic));
        const questionBox = div.querySelector(".tree-questions");
        const questionsToShow = topicMatches ? (topic.questions || []) : matchingQuestions;
        questionsToShow.forEach(question=>{
            const qDiv = document.createElement("div"); qDiv.className = "tree-question"; qDiv.innerHTML = highlightMatch(question, lowerQuery);
            qDiv.addEventListener("click", ()=>{
                document.querySelectorAll(".tree-question").forEach(q => q.classList.remove("active"));
                qDiv.classList.add("active");
                askQuestion(question);
            });
            questionBox.appendChild(qDiv);
        });
        container.appendChild(div);
    });
    if(!matchedAny) container.innerHTML = `<div class="tree-empty">No nodes matched.</div>`;
}

async function filterKnowledgeTree(rawQuery){
    const lowerQuery = rawQuery.trim().toLowerCase();
    searchClearButton.classList.toggle("hidden", lowerQuery === "");
    if(!lowerQuery){ resetKnowledgeTree(); return; }
    if(treeReadyPromise) { try{ await treeReadyPromise; } catch(error){} }
    let anyModuleMatched = false;
    state.modules.forEach(module=>{
        const moduleCard = getModuleCard(module.module);
        if(!moduleCard) return;
        const topics = fullTreeCache[module.module] || [];
        const moduleNameMatches = textMatches(module.module, lowerQuery);
        const hasDescendantMatch = topics.some(topic=>{ return textMatches(topic.topic, lowerQuery) || (topic.questions || []).some(q => textMatches(q, lowerQuery)); });
        const titleEl = moduleCard.querySelector(".tree-module-title");
        if(!moduleNameMatches && !hasDescendantMatch){
            moduleCard.classList.add("search-no-match"); titleEl.textContent = module.module; return;
        }
        anyModuleMatched = true;
        moduleCard.classList.remove("search-no-match"); moduleCard.classList.add("open");
        titleEl.innerHTML = highlightMatch(module.module, moduleNameMatches ? lowerQuery : "");
        const topicsBox = moduleCard.querySelector(".tree-topics"); topicsBox.dataset.loaded = "true";
        renderSearchTopics(topicsBox, topics, lowerQuery);
    });
    let emptyNotice = moduleList.querySelector(".tree-search-empty");
    if(!anyModuleMatched){
        if(!emptyNotice){ emptyNotice = document.createElement("div"); emptyNotice.className = "tree-empty tree-search-empty"; moduleList.appendChild(emptyNotice); }
        emptyNotice.textContent = `No results found for "${rawQuery.trim()}".`;
    } else if(emptyNotice){ emptyNotice.remove(); }
}

function resetKnowledgeTree(){
    const emptyNotice = moduleList.querySelector(".tree-search-empty");
    if(emptyNotice) emptyNotice.remove();
    document.querySelectorAll(".tree-module").forEach(card=>{
        card.classList.remove("search-no-match", "open");
        const titleEl = card.querySelector(".tree-module-title");
        if(titleEl) titleEl.textContent = card.dataset.moduleName;
        const topicsBox = card.querySelector(".tree-topics");
        if(topicsBox){ topicsBox.innerHTML = ""; delete topicsBox.dataset.loaded; }
    });
}

searchBox.addEventListener("input", ()=>{
    clearTimeout(searchDebounce);
    const value = searchBox.value;
    searchDebounce = setTimeout(()=>{ filterKnowledgeTree(value); }, 200);
});

searchBox.addEventListener("keydown", (event)=>{ if(event.key === "Escape"){ searchBox.value = ""; filterKnowledgeTree(""); }});
searchClearButton.addEventListener("click", ()=>{ searchBox.value = ""; filterKnowledgeTree(""); searchBox.focus(); });


/*=========================================================
    UI ENHANCEMENT ADD-ONS (Pure Visual Polish)
=========================================================*/
(function initUIEnhancements() {
    // 1. Particle Background System
    const canvas = document.getElementById("okai-canvas-bg");
    if(canvas) {
        const ctx = canvas.getContext("2d");
        let particles = [];
        
        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        window.addEventListener("resize", resize);
        resize();

        class Particle {
            constructor() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.size = Math.random() * 2;
                this.speedX = (Math.random() - 0.5) * 0.5;
                this.speedY = (Math.random() - 0.5) * 0.5;
                this.opacity = Math.random() * 0.5;
                this.color = Math.random() > 0.55 ? "255,255,255" : "255,145,70";
            }
            update() {
                this.x += this.speedX;
                this.y += this.speedY;
                if (this.x < 0 || this.x > canvas.width) this.speedX *= -1;
                if (this.y < 0 || this.y > canvas.height) this.speedY *= -1;
            }
            draw() {
                ctx.fillStyle = `rgba(${this.color}, ${this.opacity})`;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }
        
        for (let i = 0; i < 100; i++) particles.push(new Particle());
        
        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach(p => { p.update(); p.draw(); });
            requestAnimationFrame(animate);
        }
        animate();
    }

    // 2. Ripple Effect Logic
    document.addEventListener("click", (e) => {
        const btn = e.target.closest(".ripple");
        if (btn) {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const ripple = document.createElement("span");
            ripple.className = "ripple-effect";
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            ripple.style.width = ripple.style.height = `${Math.max(rect.width, rect.height)}px`;
            btn.appendChild(ripple);
            setTimeout(() => ripple.remove(), 600);
        }
    });

    // Single subtle cursor glow only; no magnetic pull or hover sparkle layer.
    const cursor = document.getElementById("magnet-cursor");
    if (cursor && window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
        document.addEventListener("pointermove", (e) => {
            cursor.style.left = `${e.clientX}px`;
            cursor.style.top = `${e.clientY}px`;
        });
    }
})();