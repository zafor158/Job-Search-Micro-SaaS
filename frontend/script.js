// updated version for both manual input and uploaded pdf modification
document.addEventListener('DOMContentLoaded', () => {
    // --- Get all necessary HTML elements ---
    const profileForm = document.getElementById("profileForm");
    const uploadSection = document.getElementById("uploadSection");
    const uploadBtn = document.getElementById("uploadBtn");
    const resumeFileInput = document.getElementById("resumeFile");
    
    const modificationZone = document.getElementById("modificationZone");
    const modificationForm = document.getElementById("modificationForm");
    const parsedTextPreview = document.getElementById("parsedTextPreview");

    const resumeContainer = document.getElementById("resumeContainer");
    const downloadBtn = document.getElementById("downloadBtn");

    // --- State variables to hold data between steps ---
    let extractedResumeText = null;
    let finalResumeData = null;

    // --- WORKFLOW 1: Manual Form Submission ---
    profileForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(profileForm);
        const data = Object.fromEntries(formData.entries());

        resumeContainer.innerHTML = "Generating Resume...";
        downloadBtn.style.display = 'none';

        try {
            // NOTE: The endpoint for the form is '/generate_resume'
            const response = await fetch("http://127.0.0.1:8000/generate_resume", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });
            
            if (!response.ok) throw new Error(`Server error: ${response.statusText}`);

            finalResumeData = await response.json();
            displayResumePreview(finalResumeData);
            downloadBtn.style.display = 'block';

        } catch (err) {
            resumeContainer.innerHTML = `<p style="color:red;">Error generating resume: ${err.message}</p>`;
        }
    });

    // --- WORKFLOW 2, STEP 1: PDF Upload & Parse ---
    uploadBtn.addEventListener('click', async () => {
        const file = resumeFileInput.files[0];
        if (!file) {
            alert("Please select a PDF file to upload.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);
        resumeContainer.innerHTML = "Parsing your resume...";

        try {
            const response = await fetch("http://127.0.0.1:8000/upload/pdf", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) throw new Error(`Server error: ${response.statusText}`);

            const result = await response.json();
            extractedResumeText = result.extracted_text;

            // Hide the initial forms and show the modification Q&A section
            profileForm.style.display = 'none';
            uploadSection.style.display = 'none';
            modificationZone.style.display = 'block';
            parsedTextPreview.innerText = `Extracted Text Preview:\n"${extractedResumeText.substring(0, 250)}..."`;
            resumeContainer.innerHTML = "";

        } catch (err) {
            resumeContainer.innerHTML = `<p style="color:red;">Error parsing PDF: ${err.message}</p>`;
        }
    });

    // --- WORKFLOW 2, STEP 2: Guided Modification & Generation ---
    modificationForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const modData = new FormData(modificationForm);
        const modificationAnswers = Object.fromEntries(modData.entries());

        const requestBody = {
            extracted_text: extractedResumeText,
            modification_instructions: modificationAnswers
        };

        resumeContainer.innerHTML = "Applying modifications and generating new resume...";
        downloadBtn.style.display = 'none';

        try {
            // NOTE: The endpoint for this step is '/generate_modified_resume'
            const response = await fetch("http://127.0.0.1:8000/generate_modified_resume", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(requestBody),
            });

            if (!response.ok) throw new Error(`Server error: ${response.statusText}`);

            finalResumeData = await response.json();
            displayResumePreview(finalResumeData);
            downloadBtn.style.display = 'block';

        } catch (err) {
            resumeContainer.innerHTML = `<p style="color:red;">Error generating resume: ${err.message}</p>`;
        }
    });

    // --- FINAL STEP: PDF Download (Used by both workflows) ---
    downloadBtn.addEventListener("click", async () => {
        if (!finalResumeData) return alert("No resume data to download.");

        try {
            const response = await fetch("http://127.0.0.1:8000/export/pdf", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(finalResumeData),
            });

            if (!response.ok) throw new Error(`PDF generation failed`);

            const pdfBlob = await response.blob();
            const url = window.URL.createObjectURL(pdfBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'Generated_Resume.pdf';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            alert(`Could not download PDF: ${err.message}`);
        }
    });

    // --- Helper function to display the final resume preview ---
    function displayResumePreview(data) {
        const experienceHtml = (data.experience || []).map(job => `
            <h4>${job.title || ''} at ${job.company || ''} (${job.dates || ''})</h4>
            <ul>${(job.bullets || []).map(b => `<li>${b}</li>`).join('')}</ul>
        `).join('');

        resumeContainer.innerHTML = `
            <h3>${data.name || 'Name not found'}</h3>
            <p>${data.email || ''} | ${data.phone || ''}</p>
            <h4>Summary</h4>
            <p>${data.summary || 'Not generated.'}</p>
            <h4>Experience</h4>
            ${experienceHtml}
            <h4>Education</h4>
            <p>${data.education || 'Not found.'}</p>
            <h4>Skills</h4>
            <p>${(data.skills || []).join(', ')}</p>
        `;
    }
});

//new version
// document.addEventListener('DOMContentLoaded', () => {
//     const form = document.getElementById("profileForm");
//     const resumeContainer = document.getElementById("resumeContainer");
//     const downloadBtn = document.getElementById("downloadBtn");
    
//     // This variable will hold the final data for the PDF
//     let finalResumeData = null;

//     form.addEventListener("submit", async (e) => {
//         e.preventDefault();
//         const formData = new FormData(form);
//         const data = Object.fromEntries(formData.entries());

//         resumeContainer.innerHTML = "Generating Resume...";
//         downloadBtn.style.display = 'none';

//         try {
//             const response = await fetch("http://127.0.0.1:8000/generate_resume", {
//                 method: "POST",
//                 headers: { "Content-Type": "application/json" },
//                 body: JSON.stringify(data),
//             });
            
//             if (!response.ok) {
//                 throw new Error(`Server error: ${response.statusText}`);
//             }

//             finalResumeData = await response.json();
//             displayResumePreview(finalResumeData);
//             downloadBtn.style.display = 'block'; // Show the download button

//         } catch (err) {
//             resumeContainer.innerHTML = `<p style="color:red;">Error generating resume: ${err.message}</p>`;
//             console.error(err);
//         }
//     });

//     downloadBtn.addEventListener("click", async () => {
//         if (!finalResumeData) {
//             alert("No resume data to download. Please generate first.");
//             return;
//         }

//         try {
//             const response = await fetch("http://127.0.0.1:8000/export/pdf", {
//                 method: "POST",
//                 headers: { "Content-Type": "application/json" },
//                 body: JSON.stringify(finalResumeData),
//             });

//             if (!response.ok) {
//                 throw new Error(`PDF generation failed: ${response.statusText}`);
//             }

//             const pdfBlob = await response.blob();
//             const url = window.URL.createObjectURL(pdfBlob);
//             const a = document.createElement('a');
//             a.href = url;
//             a.download = 'resume.pdf';
//             document.body.appendChild(a);
//             a.click();
//             a.remove();
//             window.URL.revokeObjectURL(url);
            
//         } catch (err) {
//             alert(`Could not download PDF: ${err.message}`);
//             console.error(err);
//         }
//     });

//     function displayResumePreview(data) {
//         let experienceHtml = data.experience.map(job => `
//             <h4>${job.title} at ${job.company} (${job.dates})</h4>
//             <ul>${job.bullets.map(b => `<li>${b}</li>`).join('')}</ul>
//         `).join('');

//         resumeContainer.innerHTML = `
//             <h3>${data.name}</h3>
//             <p>${data.email} | ${data.phone}</p>
//             <h4>Summary</h4>
//             <p>${data.summary}</p>
//             <h4>Experience</h4>
//             ${experienceHtml}
//             <h4>Education</h4>
//             <p>${data.education}</p>
//             <h4>Skills</h4>
//             <p>${data.skills.join(', ')}</p>
//         `;
//     }
// });

// const form = document.getElementById("profileForm");
// const resumeContainer = document.getElementById("resumeContainer");
// const downloadBtn = document.getElementById("downloadBtn");

// form.addEventListener("submit", async (e) => {
//     e.preventDefault();

//     const formData = new FormData(form);
//     const data = Object.fromEntries(formData.entries());

//     resumeContainer.innerHTML = "Generating Resume...";

//     try {
//         const response = await fetch("http://127.0.0.1:8000/generate_resume", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify(data),
//         });

//         const result = await response.json();
//         resumeContainer.innerHTML = result.resume_html;

//     } catch (err) {
//         resumeContainer.innerHTML = "Error generating resume.";
//         console.error(err);
//     }
// });

// // Download as PDF
// downloadBtn.addEventListener("click", () => {
//     const element = resumeContainer;
//     const opt = {
//         margin:       0.5,
//         filename:     'resume.pdf',
//         image:        { type: 'jpeg', quality: 0.98 },
//         html2canvas:  { scale: 2 },
//         jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
//     };
//     html2pdf().from(element).set(opt).save();
// });