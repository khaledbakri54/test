// State
let currentStep = 1;
const totalSteps = 5;

// Navigation
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
    document.getElementById(sectionId).style.display = 'block';

    document.querySelectorAll('.nav-links a').forEach(a => {
        a.classList.toggle('active', a.getAttribute('href') === '#' + sectionId);
    });

    if (sectionId === 'manage') {
        renderDocumentsList();
    }

    if (sectionId === 'create') {
        resetForm();
    }

    window.scrollTo(0, 0);
}

// Nav link click handling
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', function (e) {
        e.preventDefault();
        const sectionId = this.getAttribute('href').substring(1);
        showSection(sectionId);
    });
});

// Multi-step form
function changeStep(direction) {
    const currentFields = document.querySelector(`.form-step[data-step="${currentStep}"]`);

    if (direction === 1 && currentStep < totalSteps) {
        if (!validateStep(currentStep)) return;
    }

    currentStep += direction;
    currentStep = Math.max(1, Math.min(totalSteps, currentStep));

    document.querySelectorAll('.form-step').forEach(s => s.classList.remove('active'));
    document.querySelector(`.form-step[data-step="${currentStep}"]`).classList.add('active');

    updateProgressBar();
    updateButtons();

    if (currentStep === totalSteps) {
        renderReview();
    }
}

function updateProgressBar() {
    document.querySelectorAll('.progress-step').forEach(step => {
        const stepNum = parseInt(step.dataset.step);
        step.classList.remove('active', 'completed');
        if (stepNum === currentStep) step.classList.add('active');
        else if (stepNum < currentStep) step.classList.add('completed');
    });
}

function updateButtons() {
    document.getElementById('prevBtn').style.display = currentStep > 1 ? 'inline-flex' : 'none';
    document.getElementById('nextBtn').style.display = currentStep < totalSteps ? 'inline-flex' : 'none';
    document.getElementById('submitBtn').style.display = currentStep === totalSteps ? 'inline-flex' : 'none';
}

function validateStep(step) {
    const stepEl = document.querySelector(`.form-step[data-step="${step}"]`);
    const required = stepEl.querySelectorAll('[required]');
    let valid = true;

    required.forEach(input => {
        input.classList.remove('error');
        if (!input.value.trim()) {
            input.classList.add('error');
            valid = false;
        }
    });

    if (!valid) {
        const firstError = stepEl.querySelector('.error');
        if (firstError) firstError.focus();
    }

    return valid;
}

function resetForm() {
    currentStep = 1;
    document.getElementById('poa-form').reset();
    document.querySelectorAll('.form-step').forEach(s => s.classList.remove('active'));
    document.querySelector('.form-step[data-step="1"]').classList.add('active');
    updateProgressBar();
    updateButtons();

    // Set default expiration to 1 year from now
    const expDate = new Date();
    expDate.setFullYear(expDate.getFullYear() + 1);
    document.getElementById('expirationDate').value = expDate.toISOString().split('T')[0];
}

// Get form data
function getFormData() {
    const form = document.getElementById('poa-form');
    const data = {};
    new FormData(form).forEach((value, key) => {
        data[key] = value;
    });
    return data;
}

// POA type labels
const poaTypeLabels = {
    sale: 'Vehicle Sale',
    registration: 'Vehicle Registration',
    title_transfer: 'Title Transfer',
    general: 'General Vehicle POA'
};

// Render review
function renderReview() {
    const data = getFormData();
    const html = `
        <div class="review-section">
            <h4>POA Type</h4>
            <div class="review-row">
                <span class="review-label">Type</span>
                <span class="review-value">${poaTypeLabels[data.poaType] || data.poaType}</span>
            </div>
            <div class="review-row">
                <span class="review-label">Expires</span>
                <span class="review-value">${formatDate(data.expirationDate)}</span>
            </div>
        </div>
        <div class="review-section">
            <h4>Principal (Vehicle Owner)</h4>
            <div class="review-row">
                <span class="review-label">Name</span>
                <span class="review-value">${esc(data.principalFirstName)} ${esc(data.principalLastName)}</span>
            </div>
            <div class="review-row">
                <span class="review-label">Address</span>
                <span class="review-value">${esc(data.principalAddress)}, ${esc(data.principalCity)}, ${esc(data.principalState)} ${esc(data.principalZip)}</span>
            </div>
            <div class="review-row">
                <span class="review-label">Phone</span>
                <span class="review-value">${esc(data.principalPhone)}</span>
            </div>
            <div class="review-row">
                <span class="review-label">ID Number</span>
                <span class="review-value">${esc(data.principalId)}</span>
            </div>
        </div>
        <div class="review-section">
            <h4>Attorney-in-Fact</h4>
            <div class="review-row">
                <span class="review-label">Name</span>
                <span class="review-value">${esc(data.attorneyFirstName)} ${esc(data.attorneyLastName)}</span>
            </div>
            <div class="review-row">
                <span class="review-label">Address</span>
                <span class="review-value">${esc(data.attorneyAddress)}, ${esc(data.attorneyCity)}, ${esc(data.attorneyState)} ${esc(data.attorneyZip)}</span>
            </div>
            <div class="review-row">
                <span class="review-label">Phone</span>
                <span class="review-value">${esc(data.attorneyPhone)}</span>
            </div>
            <div class="review-row">
                <span class="review-label">ID Number</span>
                <span class="review-value">${esc(data.attorneyId)}</span>
            </div>
            <div class="review-row">
                <span class="review-label">Relationship</span>
                <span class="review-value">${esc(data.relationship) || 'N/A'}</span>
            </div>
        </div>
        <div class="review-section">
            <h4>Vehicle</h4>
            <div class="review-row">
                <span class="review-label">Vehicle</span>
                <span class="review-value">${esc(data.vehicleYear)} ${esc(data.vehicleMake)} ${esc(data.vehicleModel)}</span>
            </div>
            <div class="review-row">
                <span class="review-label">VIN</span>
                <span class="review-value">${esc(data.vehicleVin)}</span>
            </div>
            <div class="review-row">
                <span class="review-label">Color</span>
                <span class="review-value">${esc(data.vehicleColor) || 'N/A'}</span>
            </div>
            <div class="review-row">
                <span class="review-label">Plate</span>
                <span class="review-value">${esc(data.vehiclePlate) || 'N/A'} ${esc(data.vehiclePlateState) || ''}</span>
            </div>
            ${data.additionalTerms ? `
            <div class="review-row" style="flex-direction: column; gap: 0.3rem;">
                <span class="review-label">Additional Terms</span>
                <span class="review-value" style="text-align: left;">${esc(data.additionalTerms)}</span>
            </div>` : ''}
        </div>
    `;
    document.getElementById('review-content').innerHTML = html;
}

// Submit POA
function submitPOA() {
    const ack = document.getElementById('ackCheckbox');
    if (!ack.checked) {
        ack.focus();
        return;
    }

    const data = getFormData();
    data.id = Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
    data.createdAt = new Date().toISOString();

    const docs = getStoredDocs();
    docs.push(data);
    localStorage.setItem('autopoa_docs', JSON.stringify(docs));

    showSection('manage');
}

// Storage helpers
function getStoredDocs() {
    try {
        return JSON.parse(localStorage.getItem('autopoa_docs') || '[]');
    } catch {
        return [];
    }
}

function deleteDocument(id) {
    const docs = getStoredDocs().filter(d => d.id !== id);
    localStorage.setItem('autopoa_docs', JSON.stringify(docs));
    renderDocumentsList();
}

// Render documents list
function renderDocumentsList() {
    const docs = getStoredDocs();
    const container = document.getElementById('documents-list');

    if (docs.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">&#128194;</div>
                <h3>No documents yet</h3>
                <p>Create your first Vehicle Power of Attorney to get started.</p>
                <button class="btn btn-primary" onclick="showSection('create')">Create New POA</button>
            </div>`;
        return;
    }

    container.innerHTML = docs.map(doc => {
        const isExpired = new Date(doc.expirationDate) < new Date();
        return `
            <div class="document-card">
                <div class="doc-info">
                    <h4>${esc(poaTypeLabels[doc.poaType] || doc.poaType)}</h4>
                    <p>${esc(doc.vehicleYear)} ${esc(doc.vehicleMake)} ${esc(doc.vehicleModel)} &mdash; VIN: ${esc(doc.vehicleVin)}</p>
                    <div class="doc-meta">
                        <span class="doc-badge ${isExpired ? 'badge-expired' : 'badge-active'}">${isExpired ? 'Expired' : 'Active'}</span>
                        <span style="font-size:0.8rem;color:var(--text-light)">Created ${formatDate(doc.createdAt)}</span>
                    </div>
                </div>
                <div class="doc-actions">
                    <button class="btn btn-secondary btn-sm" onclick="viewDocument('${doc.id}')">View</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteDocument('${doc.id}')">Delete</button>
                </div>
            </div>`;
    }).join('');
}

// View document (modal with printable POA)
function viewDocument(id) {
    const doc = getStoredDocs().find(d => d.id === id);
    if (!doc) return;

    const poaDescription = getPoaDescription(doc);

    const html = `
        <div class="doc-preview" id="printable-doc">
            <div class="doc-title">Power of Attorney</div>
            <div class="doc-subtitle">Vehicle Transaction Authorization</div>

            <p><strong>Document ID:</strong> ${esc(doc.id)}<br>
            <strong>Date Created:</strong> ${formatDate(doc.createdAt)}<br>
            <strong>Expiration Date:</strong> ${formatDate(doc.expirationDate)}</p>

            <p>I, <strong>${esc(doc.principalFirstName)} ${esc(doc.principalLastName)}</strong>,
            residing at ${esc(doc.principalAddress)}, ${esc(doc.principalCity)}, ${esc(doc.principalState)} ${esc(doc.principalZip)},
            ID Number: ${esc(doc.principalId)}, (hereinafter referred to as the "Principal"),
            do hereby appoint:</p>

            <p><strong>${esc(doc.attorneyFirstName)} ${esc(doc.attorneyLastName)}</strong>,
            residing at ${esc(doc.attorneyAddress)}, ${esc(doc.attorneyCity)}, ${esc(doc.attorneyState)} ${esc(doc.attorneyZip)},
            ID Number: ${esc(doc.attorneyId)}${doc.relationship ? ', Relationship: ' + esc(doc.relationship) : ''},
            (hereinafter referred to as the "Attorney-in-Fact"),</p>

            <p>as my true and lawful Attorney-in-Fact, to act on my behalf with respect to the following described vehicle:</p>

            <p><strong>Year:</strong> ${esc(doc.vehicleYear)} &nbsp;
            <strong>Make:</strong> ${esc(doc.vehicleMake)} &nbsp;
            <strong>Model:</strong> ${esc(doc.vehicleModel)}<br>
            <strong>VIN:</strong> ${esc(doc.vehicleVin)}
            ${doc.vehicleColor ? '<br><strong>Color:</strong> ' + esc(doc.vehicleColor) : ''}
            ${doc.vehiclePlate ? '<br><strong>License Plate:</strong> ' + esc(doc.vehiclePlate) + ' (' + esc(doc.vehiclePlateState || '') + ')' : ''}
            ${doc.vehicleMileage ? '<br><strong>Mileage:</strong> ' + esc(doc.vehicleMileage) : ''}
            ${doc.vehicleTitleNumber ? '<br><strong>Title Number:</strong> ' + esc(doc.vehicleTitleNumber) : ''}
            </p>

            <p>${poaDescription}</p>

            ${doc.additionalTerms ? '<p><strong>Additional Terms:</strong> ' + esc(doc.additionalTerms) + '</p>' : ''}

            <p>This Power of Attorney shall be effective as of the date signed below and shall remain in effect until
            <strong>${formatDate(doc.expirationDate)}</strong>, unless sooner revoked by the Principal in writing.</p>

            <p>The Principal hereby grants the Attorney-in-Fact full power and authority to do and perform all acts necessary
            to carry out the purposes described above, including but not limited to signing documents, appearing before
            government agencies, and taking any other action reasonably required.</p>

            <div class="sig-block">
                <div>
                    <div class="sig-line">Principal Signature</div>
                    <p>${esc(doc.principalFirstName)} ${esc(doc.principalLastName)}</p>
                    <p>Date: _______________</p>
                </div>
                <div>
                    <div class="sig-line">Attorney-in-Fact Signature</div>
                    <p>${esc(doc.attorneyFirstName)} ${esc(doc.attorneyLastName)}</p>
                    <p>Date: _______________</p>
                </div>
            </div>

            <div class="notary-block">
                <h4>Notary Acknowledgment</h4>
                <p>State of _______________&nbsp;&nbsp;&nbsp;County of _______________</p>
                <p>On this _____ day of _______________, 20____, before me, the undersigned notary public,
                personally appeared the above-named Principal, known to me (or proved to me on the basis of
                satisfactory evidence) to be the person whose name is subscribed to the within instrument and
                acknowledged to me that they executed the same in their authorized capacity.</p>
                <div class="sig-line" style="max-width: 300px; margin-top: 3rem;">Notary Public</div>
                <p style="margin-top: 0.5rem;">My Commission Expires: _______________</p>
            </div>
        </div>
    `;

    document.getElementById('modal-body').innerHTML = html;
    document.getElementById('preview-modal').style.display = 'flex';
}

function getPoaDescription(doc) {
    const descriptions = {
        sale: `The Attorney-in-Fact is hereby authorized to sell, transfer, and convey the above-described vehicle on behalf of the Principal. This includes negotiating terms of sale, executing bills of sale, endorsing and delivering the certificate of title, and performing any other acts necessary to complete the sale of the vehicle.`,
        registration: `The Attorney-in-Fact is hereby authorized to register, renew registration, or make any changes to the registration of the above-described vehicle on behalf of the Principal. This includes appearing at the Department of Motor Vehicles, signing registration documents, paying required fees, and performing any other acts necessary to complete the registration process.`,
        title_transfer: `The Attorney-in-Fact is hereby authorized to transfer the title of the above-described vehicle on behalf of the Principal. This includes endorsing and delivering the certificate of title, applying for a new or duplicate title, signing title transfer documents, and performing any other acts necessary to complete the title transfer.`,
        general: `The Attorney-in-Fact is hereby authorized to perform any and all acts related to the above-described vehicle on behalf of the Principal. This includes, but is not limited to, selling, purchasing, registering, transferring title, insuring, maintaining, and otherwise managing the vehicle. The Attorney-in-Fact may sign any documents, appear before any government agencies, and take any other action reasonably necessary in connection with the vehicle.`
    };
    return descriptions[doc.poaType] || descriptions.general;
}

function closeModal() {
    document.getElementById('preview-modal').style.display = 'none';
}

function printDocument() {
    const content = document.getElementById('printable-doc').innerHTML;
    const win = window.open('', '_blank');
    win.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Power of Attorney</title>
            <style>
                body { font-family: Georgia, serif; max-width: 800px; margin: 2rem auto; padding: 0 2rem; line-height: 1.8; color: #1f2937; }
                .doc-title { text-align: center; font-size: 1.5rem; font-weight: bold; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 0.5rem; }
                .doc-subtitle { text-align: center; color: #6b7280; margin-bottom: 2rem; font-style: italic; }
                p { margin-bottom: 1rem; text-align: justify; }
                .sig-block { margin-top: 3rem; display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
                .sig-line { border-top: 1px solid #1f2937; padding-top: 0.3rem; margin-top: 3rem; font-size: 0.9rem; }
                .notary-block { margin-top: 3rem; padding: 1.5rem; border: 1px solid #d1d5db; border-radius: 8px; }
                .notary-block h4 { margin-bottom: 1rem; text-align: center; }
                @media print { body { margin: 0; } }
            </style>
        </head>
        <body>${content}</body>
        </html>
    `);
    win.document.close();
    win.print();
}

// FAQ toggle
function toggleFaq(button) {
    const answer = button.nextElementSibling;
    const isOpen = answer.classList.contains('open');

    document.querySelectorAll('.faq-answer').forEach(a => a.classList.remove('open'));
    document.querySelectorAll('.faq-question').forEach(q => q.classList.remove('open'));

    if (!isOpen) {
        answer.classList.add('open');
        button.classList.add('open');
    }
}

// Utility: HTML escape
function esc(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// Utility: format date
function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
}

// Close modal on backdrop click
document.getElementById('preview-modal').addEventListener('click', function (e) {
    if (e.target === this) closeModal();
});

// Set default expiration date on load
document.addEventListener('DOMContentLoaded', function () {
    const expDate = new Date();
    expDate.setFullYear(expDate.getFullYear() + 1);
    document.getElementById('expirationDate').value = expDate.toISOString().split('T')[0];
});
