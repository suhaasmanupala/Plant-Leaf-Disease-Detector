
document.addEventListener('DOMContentLoaded', () => {
    // Drag-and-Drop Upload
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file');
    const cameraInput = document.getElementById('camera-file');
    const cameraBtn = document.getElementById('camera-btn');
    const previewImg = document.getElementById('preview-img');
    
    uploadZone.addEventListener('click', () => fileInput.click());
    
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });
    
    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });
    
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        fileInput.files = e.dataTransfer.files;
        previewImage(e.dataTransfer.files[0]);
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files[0]) {
            previewImage(fileInput.files[0]);
        }
    });

    cameraBtn.addEventListener('click', () => cameraInput.click());
    cameraInput.addEventListener('change', () => {
        if (cameraInput.files[0]) {
            fileInput.files = cameraInput.files;
            previewImage(cameraInput.files[0]);
        }
    });

    function previewImage(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            previewImg.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }

    // Progress Spinner (Simulated)
    const form = document.getElementById('predict');
    const spinner = document.getElementById('progress-spinner');
    const progressPercent = document.getElementById('progress-percent');
    
    form.addEventListener('submit', () => {
        spinner.classList.remove('hidden');
        let percent = 0;
        const interval = setInterval(() => {
            percent += 10;
            progressPercent.textContent = `${percent}%`;
            if (percent >= 100) clearInterval(interval);
        }, 200);
    });

    // Heatmap Toggle
    const heatmapToggle = document.getElementById('heatmap-toggle');
    const heatmapOverlay = document.getElementById('heatmap-overlay');
    
    if (heatmapToggle) {
        heatmapToggle.addEventListener('click', () => {
            const isActive = heatmapOverlay.classList.toggle('active');
            heatmapToggle.textContent = isActive ? translations[languageSelect.value]['hide-heatmap'] || 'Hide Heatmap' : translations[languageSelect.value]['show-heatmap'] || 'Show Heatmap';
        });
    }

    // Scientific Details Toggle
    const scientificToggle = document.getElementById('scientific-toggle');
    const scientificDetails = document.getElementById('scientific-details');
    
    if (scientificToggle) {
        scientificToggle.addEventListener('click', () => {
            const isActive = scientificDetails.classList.toggle('hidden');
            scientificToggle.textContent = isActive ? translations[languageSelect.value]['show-scientific'] || 'Show Advanced Details' : translations[languageSelect.value]['hide-scientific'] || 'Hide Advanced Details';
        });
    }

    // Theme Toggle
    const themeToggle = document.querySelector('.theme-toggle');
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
    });

    // Share Button
    const shareBtn = document.querySelector('.share-btn');
    if (shareBtn) {
        shareBtn.addEventListener('click', async () => {
            const resultText = shareBtn.dataset.result;
            if (navigator.share) {
                try {
                    await navigator.share({
                        title: 'Plant Disease Diagnosis',
                        text: resultText,
                        url: window.location.href
                    });
                } catch (err) {
                    console.error('Share failed:', err);
                }
            } else {
                navigator.clipboard.writeText(resultText).then(() => {
                    alert('Result copied to clipboard!');
                });
            }
        });
    }

    // Language Toggle
    const translations = {
        en: {
            'hero-title': 'Plant Leaf Disease Detector',
            'hero-desc': 'Upload a leaf photo to instantly detect diseases and get natural treatment tips.',
            'try-now': 'Try Now',
            'select-species': 'Select Plant Species:',
            'upload-text': 'Drag & Drop Leaf Image or Click to Upload',
            'camera-btn': 'Take Photo from Camera',
            'processing': 'Processing...',
            'predict-btn': 'Predict Disease',
            'uploaded-image': 'Uploaded Leaf Image:',
            'show-heatmap': 'Show Heatmap',
            'hide-heatmap': 'Hide Heatmap',
            'prediction': 'Prediction:',
            'confidence': 'Confidence:',
            'organic-remedies': 'Organic Remedies',
            'chemical-remedies': 'Chemical Remedies',
            'preventive-measures': 'Preventive Measures',
            'organic-tooltip': 'Use organic compost to boost plant immunity.',
            'chemical-tooltip': 'Follow safety guidelines when applying chemicals.',
            'preventive-tooltip': 'Regular monitoring prevents disease spread.',
            'show-scientific': 'Show Advanced Details',
            'hide-scientific': 'Hide Advanced Details',
            'scientific-details': 'Scientific Details',
            'scientific-name': 'Scientific Name:',
            'cause': 'Cause:',
            'chemical-compounds': 'Chemical Compounds:',
            'save-garden': 'Save to My Garden',
            'share-result': 'Share Result',
            'login': 'Login',
            'logout': 'Logout',
            'my-garden': 'My Garden',
            'username': 'Username',
            'password': 'Password',
            'register': 'Register',
            'have-account': 'Already have an account?',
            'no-detections': 'No detections saved yet.',
            'back-home': 'Back to Home',
            'past-detections': 'Past Detections',
            'language': 'Language:'
        },
        hi: {
            'hero-title': 'पौधे की पत्ती रोग डिटेक्टर',
            'hero-desc': 'पत्ती की फोटो अपलोड करें और तुरंत रोगों का पता लगाएं और प्राकृतिक उपचार युक्तियाँ प्राप्त करें।',
            'try-now': 'अब आज़माएं',
            'select-species': 'पौधे की प्रजाति चुनें:',
            'upload-text': 'पत्ती की छवि ड्रैग और ड्रॉप करें या क्लिक करके अपलोड करें',
            'camera-btn': 'कैमरे से फोटो लें',
            'processing': 'प्रसंस्करण...',
            'predict-btn': 'रोग का अनुमान लगाएं',
            'uploaded-image': 'अपलोड की गई पत्ती की छवि:',
            'show-heatmap': 'हीटमैप दिखाएं',
            'hide-heatmap': 'हीटमैप छिपाएं',
            'prediction': 'अनुमान:',
            'confidence': 'विश्वास:',
            'organic-remedies': 'जैविक उपचार',
            'chemical-remedies': 'रासायनिक उपचार',
            'preventive-measures': 'निवारक उपाय',
            'organic-tooltip': 'पौधे की प्रतिरक्षा बढ़ाने के लिए जैविक खाद का उपयोग करें।',
            'chemical-tooltip': 'रसायनों का उपयोग करते समय सुरक्षा दिशानिर्देशों का पालन करें।',
            'preventive-tooltip': 'नियमित निगरानी रोग के प्रसार को रोकती है।',
            'show-scientific': 'उन्नत विवरण दिखाएं',
            'hide-scientific': 'उन्नत विवरण छिपाएं',
            'scientific-details': 'वैज्ञानिक विवरण',
            'scientific-name': 'वैज्ञानिक नाम:',
            'cause': 'कारण:',
            'chemical-compounds': 'रासायनिक यौगिक:',
            'save-garden': 'मेरे बगीचे में सहेजें',
            'share-result': 'परिणाम साझा करें',
            'login': 'लॉगिन',
            'logout': 'लॉगआउट',
            'my-garden': 'मेरा बगीचा',
            'username': 'उपयोगकर्ता नाम',
            'password': 'पासवर्ड',
            'register': 'रजिस्टर',
            'have-account': 'पहले से खाता है?',
            'no-detections': 'अभी तक कोई डिटेक्शन सहेजा नहीं गया।',
            'back-home': 'होम पर वापस जाएं',
            'past-detections': 'पिछले डिटेक्शन',
            'language': 'भाषा:'
        },
        te: {
            'hero-title': 'ప్లాంట్ లీఫ్ డిసీజ్ డిటెక్టర్',
            'hero-desc': 'ఆకు ఫోటోను అప్‌లోడ్ చేయండి మరియు తక్షణమే వ్యాధులను గుర్తించండి మరియు సహజ చికిత్స చిట్కాలను పొందండి.',
            'try-now': 'ఇప్పుడు ప్రయత్నించండి',
            'select-species': 'మొక్క జాతిని ఎంచుకోండి:',
            'upload-text': 'ఆకు చిత్రాన్ని డ్రాగ్ చేసి డ్రాప్ చేయండి లేదా క్లిక్ చేసి అప్‌లోడ్ చేయండి',
            'camera-btn': 'కెమెరా నుండి ఫోటో తీయండి',
            'processing': 'ప్రాసెసింగ్...',
            'predict-btn': 'వ్యాధిని అంచనా వేయండి',
            'uploaded-image': 'అప్‌లోడ్ చేసిన ఆకు చిత్రం:',
            'show-heatmap': 'హీట్‌మ్యాప్ చూపించు',
            'hide-heatmap': 'హీట్‌మ్యాప్ దాచు',
            'prediction': 'అంచనా:',
            'confidence': 'విశ్వాసం:',
            'organic-remedies': 'సేంద్రీయ చికిత్సలు',
            'chemical-remedies': 'రసాయన చికిత్సలు',
            'preventive-measures': 'నివారణ చర్యలు',
            'organic-tooltip': 'మొక్క రోగనిరోధక శక్తిని పెంచడానికి సేంద్రీయ ఎరువు ఉపయోగించండి.',
            'chemical-tooltip': 'రసాయనాలను ఉపయోగించేటప్పుడు భద్రతా మార్గదర్శకాలను అనుసరించండి.',
            'preventive-tooltip': 'నియమిత పర్యవేక్షణ వ్యాధి వ్యాప్తిని నిరోధిస్తుంది.',
            'show-scientific': 'అధునాతన వివరాలను చూపించు',
            'hide-scientific': 'అధునాతన వివరాలను దాచు',
            'scientific-details': 'వైజ్ఞానిక వివరాలు',
            'scientific-name': 'వైజ్ఞానిక నామం:',
            'cause': 'కారణం:',
            'chemical-compounds': 'రసాయన సమ్మేళనాలు:',
            'save-garden': 'నా గార్డెన్‌కు సేవ్ చేయండి',
            'share-result': 'ఫలితాన్ని షేర్ చేయండి',
            'login': 'లాగిన్',
            'logout': 'లాగౌట్',
            'my-garden': 'నా గార్డెన్',
            'username': 'వినియోగదారు పేరు',
            'password': 'పాస్‌వర్డ్',
            'register': 'రిజిస్టర్',
            'have-account': 'ఇప్పటికే ఖాతా ఉందా?',
            'no-detections': 'ఇంకా డిటెక్షన్లు సేవ్ చేయబడలేదు.',
            'back-home': 'హోమ్‌కి తిరిగి వెళ్ళండి',
            'past-detections': 'గత డిటెక్షన్లు',
            'language': 'భాష:'
        }
    };

    const languageSelect = document.getElementById('language-select');
    languageSelect.addEventListener('change', () => {
        const lang = languageSelect.value;
        document.querySelectorAll('[data-i18n]').forEach(elem => {
            const key = elem.getAttribute('data-i18n');
            elem.textContent = translations[lang][key] || elem.textContent;
            if (elem.tagName === 'BUTTON' || elem.tagName === 'A') {
                const icon = elem.querySelector('i');
                if (icon) {
                    elem.textContent = translations[lang][key] || elem.textContent;
                    elem.appendChild(icon);
                }
            }
        });
    });
});
