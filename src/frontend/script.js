document.addEventListener('DOMContentLoaded', () => {
    // ─── DOM References ───
    const codeInput = document.getElementById('codeInput');
    const fileUpload = document.getElementById('fileUpload');
    const fileStatus = document.getElementById('fileStatus');
    const convertBtn = document.getElementById('convertBtn');
    const clearBtn = document.getElementById('clearBtn');
    const tableBody = document.getElementById('tableBody');
    const tokenCount = document.getElementById('tokenCount');
    const statusMsg = document.getElementById('statusMessage');

    // ─── AUTO-GROW TEXTAREA ───
    function autoGrow() {
        codeInput.style.height = 'auto';
        codeInput.style.height = codeInput.scrollHeight + 'px';
    }

    // Listen to every keystroke, paste, cut, etc.
    codeInput.addEventListener('input', autoGrow);

    // ─── FILE INPUT HANDLER ───
    fileUpload.addEventListener('change', function (event) {
        const file = this.files[0];
        if (!file) {
            fileStatus.textContent = 'No file chosen';
            return;
        }

        //  Just the filename – no duplication!
        fileStatus.textContent = file.name;

        const ext = file.name.split('.').pop().toLowerCase();

        // --- Case 1: .docx – can't read locally, just notify ---
        if (ext === 'docx') {
            codeInput.placeholder = ` ${file.name} loaded. Click "Convert" to process.`;
            codeInput.value = ''; // Clear any manual text to avoid confusion
            autoGrow();
            setStatus('DOCX file ready. Click Convert to extract text.', '');
            return;
        }

        // --- Case 2: Text files (.txt, .py, .cpp, .c, .java) – read & populate ---
        const reader = new FileReader();
        reader.onload = function (e) {
            try {
                const content = e.target.result;
                codeInput.value = content;
                autoGrow(); //  Auto-grow after loading file content
                const lines = content.split('\n').length;
                setStatus(` Loaded ${file.name} (${lines} lines). Ready to convert.`, 'success');
            } catch (err) {
                setStatus(' Failed to read file.', 'error');
            }
        };
        reader.onerror = () => setStatus(' Error reading file.', 'error');
        reader.readAsText(file, 'UTF-8');
    });

    // ─── CONVERT BUTTON ───
    convertBtn.addEventListener('click', async function () {
        const file = fileUpload.files[0];
        const ext = file ? file.name.split('.').pop().toLowerCase() : null;

        // --- Case A: .docx file is pending → send raw to backend ---
        if (file && ext === 'docx') {
            await sendFileToBackend(file);
            return;
        }

        // --- Case B: Tokenize text from textarea ---
        const code = codeInput.value;
        if (!code || !code.trim()) {
            setStatus(' Please paste some code or upload a text file.', 'error');
            return;
        }

        await sendCodeToBackend(code);
    });

    // ─── CLEAR BUTTON ───
    clearBtn.addEventListener('click', () => {
        codeInput.value = '';
        autoGrow(); //  Shrink back to minimum
        fileUpload.value = '';
        fileStatus.textContent = 'No file chosen';
        tableBody.innerHTML = `<tr class="empty-state"><td colspan="4">Waiting for your code...</td></tr>`;
        tokenCount.textContent = '0 tokens found';
        setStatus('Cleared. Ready for new input.', '');
    });

    // ─── API: Send code to /tokenize ───
    async function sendCodeToBackend(code) {
        setStatus(' Tokenizing...', '');
        convertBtn.disabled = true;

        try {
            const response = await fetch('/tokenize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: code }),
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Server error');

            renderTable(data.tokens);
            setStatus(` Success! Found ${data.tokens.length} tokens.`, 'success');
        } catch (err) {
            setStatus(` Error: ${err.message}`, 'error');
            tableBody.innerHTML = `<tr class="empty-state"><td colspan="4">Tokenization failed</td></tr>`;
            tokenCount.textContent = '0 tokens found';
        } finally {
            convertBtn.disabled = false;
        }
    }

    // ─── API: Send .docx file to /upload ───
    async function sendFileToBackend(file) {
        setStatus(' Uploading and processing .docx...', '');
        convertBtn.disabled = true;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Server error');

            // Optionally, put the extracted text back into the textarea
            if (data.source) {
                codeInput.value = data.source;
                autoGrow(); //  Auto-grow with extracted text
            }

            renderTable(data.tokens);
            setStatus(` DOCX processed! Found ${data.tokens.length} tokens.`, 'success');
        } catch (err) {
            setStatus(` DOCX Error: ${err.message}`, 'error');
            tableBody.innerHTML = `<tr class="empty-state"><td colspan="4">File processing failed</td></tr>`;
            tokenCount.textContent = '0 tokens found';
        } finally {
            convertBtn.disabled = false;
        }
    }

    // ─── RENDER TABLE ───
    function renderTable(tokens) {
        if (!tokens || tokens.length === 0) {
            tableBody.innerHTML = `<tr class="empty-state"><td colspan="4">No tokens found</td></tr>`;
            tokenCount.textContent = '0 tokens found';
            return;
        }

        let html = '';
        tokens.forEach((t) => {
            const lexeme = escapeHtml(t.lexeme || '');
            const type = t.type || 'UNKNOWN';
            const line = t.line ?? '?';
            const col = t.col ?? '?';
            const typeClass = `token-${type}`;
            html += `<tr>
                <td><code>${lexeme}</code></td>
                <td class="${typeClass}">${type}</td>
                <td>${line}</td>
                <td>${col}</td>
            </tr>`;
        });

        tableBody.innerHTML = html;
        tokenCount.textContent = `${tokens.length} tokens found`;
    }

    // ─── HELPERS ───
    function setStatus(message, type) {
        statusMsg.textContent = message;
        statusMsg.className = 'status-message';
        if (type === 'error') statusMsg.classList.add('error');
        if (type === 'success') statusMsg.classList.add('success');
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ─── INITIAL STATE ───
    tableBody.innerHTML = `<tr class="empty-state"><td colspan="4">Waiting for your code...</td></tr>`;
    tokenCount.textContent = '0 tokens found';
    setStatus('Ready to tokenize.', '');
    autoGrow(); // Ensure textarea is sized correctly on load
});