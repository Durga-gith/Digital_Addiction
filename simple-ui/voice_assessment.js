class VoiceAssessment {
    constructor(language = 'en') {
        this.language = language;
        this.questions = [];
        this.currentQuestionIndex = 0;
        this.answers = {};
        this.isRecording = false;
        this.recognition = null;
        this.audioContext = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
        
        this.questionSets = {
            en: [
                {
                    id: 'depression',
                    text: "What is your depression level? Say a number between 0 and 30.",
                    min: 0,
                    max: 30,
                    field: 'depression'
                },
                {
                    id: 'anxiety',
                    text: "What is your anxiety level? Say a number between 0 and 30.",
                    min: 0,
                    max: 30,
                    field: 'anxiety'
                },
                {
                    id: 'stress',
                    text: "What is your stress level? Say a number between 0 and 30.",
                    min: 0,
                    max: 30,
                    field: 'stress'
                },
                {
                    id: 'selfEsteem',
                    text: "What is your self-esteem level? Say a number between 0 and 30.",
                    min: 0,
                    max: 30,
                    field: 'selfEsteem'
                },
                {
                    id: 'appUsage',
                    text: "What is your daily app usage in minutes? Say a number.",
                    min: 0,
                    max: 1440,
                    field: 'appUsage'
                },
                {
                    id: 'screenTime',
                    text: "What is your daily screen time in hours? Say a number.",
                    min: 0,
                    max: 24,
                    field: 'screenTime'
                },
                {
                    id: 'age',
                    text: "How old are you? Say your age.",
                    min: 12,
                    max: 100,
                    field: 'age'
                }
            ],
            fr: [
                {
                    id: 'depression',
                    text: "Quel est votre niveau de dépression ? Dites un nombre entre 0 et 30.",
                    min: 0,
                    max: 30,
                    field: 'depression'
                },
                {
                    id: 'anxiety',
                    text: "Quel est votre niveau d'anxiété ? Dites un nombre entre 0 et 30.",
                    min: 0,
                    max: 30,
                    field: 'anxiety'
                },
                {
                    id: 'stress',
                    text: "Quel est votre niveau de stress ? Dites un nombre entre 0 et 30.",
                    min: 0,
                    max: 30,
                    field: 'stress'
                },
                {
                    id: 'selfEsteem',
                    text: "Quel est votre niveau d'estime de soi ? Dites un nombre entre 0 et 30.",
                    min: 0,
                    max: 30,
                    field: 'selfEsteem'
                },
                {
                    id: 'appUsage',
                    text: "Quelle est votre utilisation quotidienne des applications en minutes ? Dites un nombre.",
                    min: 0,
                    max: 1440,
                    field: 'appUsage'
                },
                {
                    id: 'screenTime',
                    text: "Quel est votre temps d'écran quotidien en heures ? Dites un nombre.",
                    min: 0,
                    max: 24,
                    field: 'screenTime'
                },
                {
                    id: 'age',
                    text: "Quel âge avez-vous ? Dites votre âge.",
                    min: 12,
                    max: 100,
                    field: 'age'
                }
            ]
        };
    }

    init() {
        this.questions = this.questionSets[this.language] || this.questionSets.en;
        this.currentQuestionIndex = 0;
        this.answers = {};
        this.isRecording = false;
        
        this.initSpeechRecognition();
        
        this.updateUI();
    }

    initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = this.language === 'en' ? 'en-US' : 'fr-FR';
            this.recognition.maxAlternatives = 1;
            
            this.recognition.onstart = () => {
                console.log('Speech recognition started');
                this.updateStatus('Listening...');
            };
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                console.log('Recognized:', transcript);
                this.processSpeechResult(transcript);
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.handleRecognitionError(event.error);
            };
            
            this.recognition.onend = () => {
                console.log('Speech recognition ended');
                if (this.isRecording) {
                    setTimeout(() => {
                        if (this.isRecording) {
                            this.recognition.start();
                        }
                    }, 100);
                }
            };
        } else {
            console.warn('Speech recognition not supported');
            this.updateStatus('Speech recognition not supported in this browser');
        }
    }

    startAssessment() {
        if (!this.recognition) {
            alert('Speech recognition not available. Please use Chrome or Edge browser.');
            return;
        }
        
        this.isRecording = true;
        this.recognition.start();
        this.speakQuestion();
        this.updateUI();
    }

    stopAssessment() {
        this.isRecording = false;
        if (this.recognition) {
            this.recognition.stop();
        }
        this.updateStatus('Assessment stopped');
        this.updateUI();
    }

    speakQuestion() {
        if ('speechSynthesis' in window) {
            const currentQuestion = this.questions[this.currentQuestionIndex];
            const utterance = new SpeechSynthesisUtterance(currentQuestion.text);
            utterance.lang = this.language === 'en' ? 'en-US' : 'fr-FR';
            utterance.rate = 0.9;
            utterance.pitch = 1;
            utterance.volume = 1;
            
            utterance.onstart = () => {
                console.log('Speaking question:', currentQuestion.text);
                this.updateStatus('Asking question...');
            };
            
            utterance.onend = () => {
                console.log('Finished speaking question');
                this.updateStatus('Listening for answer...');
            };
            
            speechSynthesis.speak(utterance);
        } else {
            console.warn('Speech synthesis not supported');
            this.updateStatus('Question: ' + this.questions[this.currentQuestionIndex].text);
        }
    }

    processSpeechResult(transcript) {
        const currentQuestion = this.questions[this.currentQuestionIndex];
        const number = this.extractNumber(transcript);
        
        if (number !== null) {

            if (number >= currentQuestion.min && number <= currentQuestion.max) {

                this.answers[currentQuestion.field] = number;
                this.updateAnswerDisplay(currentQuestion.field, number);
                this.showFeedback(`Got ${number}. Next question...`, 'success');
                
                if (this.currentQuestionIndex < this.questions.length - 1) {
                    this.currentQuestionIndex++;
                    setTimeout(() => {
                        this.speakQuestion();
                        this.updateUI();
                    }, 1500);
                } else {
                    this.completeAssessment();
                }
            } else {

                this.showFeedback(`Please say a number between ${currentQuestion.min} and ${currentQuestion.max}. You said ${number}.`, 'error');
                this.speakQuestion(); 
            }
        } else {

            if (this.isUnclearResponse(transcript)) {
                this.showFeedback("I didn't catch that. Please say a number.", 'error');
                this.speakQuestion();
            } else if (this.isIDontKnowResponse(transcript)) {
                this.handleIDontKnow();
            } else {
                this.showFeedback(`I heard: "${transcript}". Please say a number between ${currentQuestion.min} and ${currentQuestion.max}.`, 'error');
                this.speakQuestion(); 
            }
        }
    }

    extractNumber(text) {

        text = text.toLowerCase().trim();

        if (this.isIDontKnowResponse(text)) {
            return null;
        }
        
        const wordToNumber = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
            'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19,
            'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
            'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90
        };
        
        if (wordToNumber[text]) {
            return wordToNumber[text];
        }
        
        const words = text.split(/\s+/);
        let total = 0;
        let current = 0;
        
        for (const word of words) {
            if (wordToNumber[word] !== undefined) {
                const value = wordToNumber[word];
                if (value >= 20 && value < 100) {
                    current = value;
                } else if (value >= 100) {
                    current *= value;
                } else {
                    current += value;
                }
            } else if (word === 'hundred') {
                current *= 100;
            }
        }
        
        if (current > 0) {
            return current;
        }
        
        const digitMatch = text.match(/\d+/);
        if (digitMatch) {
            return parseInt(digitMatch[0]);
        }
        
        return null;
    }

    isIDontKnowResponse(text) {
        const patterns = [
            /i don'?t know/i,
            /i don'?t know what to say/i,
            /i'?m not sure/i,
            /i don'?t understand/i,
            /unsure/i,
            /not sure/i
        ];
        
        if (this.language === 'fr') {
            patterns.push(
                /je ne sais pas/i,
                /je ne sais quoi dire/i,
                /je ne suis pas sûr/i,
                /pas sûr/i
            );
        }
        
        return patterns.some(pattern => pattern.test(text));
    }

    isUnclearResponse(text) {
        return text.trim().length < 2 || 
               text.toLowerCase().includes('uh') ||
               text.toLowerCase().includes('um') ||
               text.toLowerCase().includes('hmm');
    }

    handleIDontKnow() {
        const currentQuestion = this.questions[this.currentQuestionIndex];
        const fallbackValue = Math.floor((currentQuestion.min + currentQuestion.max) / 2);
        
        this.answers[currentQuestion.field] = fallbackValue;
        this.updateAnswerDisplay(currentQuestion.field, fallbackValue);
        
        this.showFeedback(`Using estimated value: ${fallbackValue}`, 'warning');
        
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(
                `Using estimated value ${fallbackValue} for ${currentQuestion.field}`
            );
            utterance.lang = this.language === 'en' ? 'en-US' : 'fr-FR';
            speechSynthesis.speak(utterance);
        }
        
        if (this.currentQuestionIndex < this.questions.length - 1) {
            this.currentQuestionIndex++;
            setTimeout(() => {
                this.speakQuestion();
                this.updateUI();
            }, 2000);
        } else {
            setTimeout(() => this.completeAssessment(), 2000);
        }
    }

    handleRecognitionError(error) {
        let errorMessage = 'Speech recognition error: ';
        
        switch(error) {
            case 'no-speech':
                errorMessage = 'No speech detected. Please try again.';
                break;
            case 'audio-capture':
                errorMessage = 'No microphone found. Please check your microphone.';
                break;
            case 'not-allowed':
                errorMessage = 'Microphone access denied. Please allow microphone access.';
                break;
            case 'network':
                errorMessage = 'Network error. Please check your internet connection.';
                break;
            default:
                errorMessage = `Error: ${error}`;
        }
        
        this.showFeedback(errorMessage, 'error');
        
        if (this.isRecording) {
            setTimeout(() => {
                if (this.isRecording) {
                    this.recognition.start();
                }
            }, 1000);
        }
    }

    completeAssessment() {
        this.isRecording = false;
        if (this.recognition) {
            this.recognition.stop();
        }
        
        this.updateStatus('Assessment complete!');
        
        this.fillFormWithAnswers();
        
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(
                this.language === 'en' 
                    ? 'Voice assessment complete. Calculating results...'
                    : 'Évaluation vocale terminée. Calcul des résultats...'
            );
            utterance.lang = this.language === 'en' ? 'en-US' : 'fr-FR';
            speechSynthesis.speak(utterance);
        }
        
        setTimeout(() => {
            this.calculateResults();
        }, 2000);
    }

    fillFormWithAnswers() {
        Object.keys(this.answers).forEach(field => {
            const value = this.answers[field];
            const element = document.getElementById(field);
            const valueElement = document.getElementById(field + 'Value');
            
            if (element) {
                element.value = value;
                if (element.type === 'range' && valueElement) {
                    valueElement.textContent = value;
                }
            }
        });
    }


    calculateResults() {

        const data = {
            depression: this.answers.depression || 15,
            anxiety: this.answers.anxiety || 15,
            stress: this.answers.stress || 15,
            selfEsteem: this.answers.selfEsteem || 20,
            appUsage: this.answers.appUsage || 180,
            screenTime: this.answers.screenTime || 5.0,
            dataUsage: 1000, 
            age: this.answers.age || 25
        };
        
        const result = this.calculateDemoResult(data);
        
        this.showResults(result);
    }

    calculateDemoResult(data) {

        const psychScore = (data.depression + data.anxiety + data.stress + (30 - data.selfEsteem)) / 120 * 100;
        
        const behaviorScore = (
            Math.min(data.appUsage / 600, 1) * 25 +
            Math.min(data.screenTime / 12, 1) * 25 +
            Math.min(data.dataUsage / 5000, 1) * 25 +
            (data.age < 25 ? 30 : data.age < 35 ? 20 : 10)
        );
        
        const totalScore = psychScore * 0.6 + behaviorScore * 0.4;
        
        let level, risk;
        if (totalScore < 30) {
            level = 'NORMAL';
            risk = totalScore / 30 * 0.3;
        } else if (totalScore < 60) {
            level = 'MODERATE';
            risk = 0.3 + (totalScore - 30) / 30 * 0.4;
        } else {
            level = 'ADDICTED';
            risk = 0.7 + (totalScore - 60) / 40 * 0.3;
        }
        
        risk = Math.min(Math.max(risk, 0), 1);
        
        const recommendations = {
            NORMAL: [
                "Maintain your current healthy digital habits",
                "Continue taking regular breaks from screens",
                "Keep practicing digital mindfulness"
            ],
            MODERATE: [
                "Consider setting daily screen time limits",
                "Try implementing a 'no phones during meals' rule",
                "Establish a digital curfew 1 hour before bed"
            ],
            ADDICTED: [
                "Seek professional help for digital addiction",
                "Consider a digital detox weekend",
                "Install app blockers to limit usage"
            ]
        };
        
        const personalized = [];
        if (data.screenTime > 8) {
            personalized.push(`Reduce screen time from ${data.screenTime} hours to under 6 hours daily`);
        }
        if (data.depression > 20) {
            personalized.push("Consider speaking with a mental health professional");
        }
        
        return {
            addiction_level: level,
            risk_score: risk,
            recommendations: [...recommendations[level], ...personalized]
        };
    }

    updateUI() {
        const currentQuestion = this.questions[this.currentQuestionIndex];
        const totalQuestions = this.questions.length;
        
        document.getElementById('questionText').textContent = currentQuestion ? currentQuestion.text : 'Assessment complete';
        document.getElementById('currentQuestionNum').textContent = this.currentQuestionIndex + 1;
        document.getElementById('totalQuestions').textContent = totalQuestions;
        
        const progressPercent = ((this.currentQuestionIndex + 1) / totalQuestions) * 100;
        document.getElementById('voiceProgressBar').style.width = `${progressPercent}%`;
        
        const voiceBtn = document.getElementById('voiceBtn');
        if (this.isRecording) {
            voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
            voiceBtn.className = 'btn voice-btn btn-danger voice-recording';
            document.getElementById('voiceStatus').textContent = 'Listening...';
        } else {
            voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            voiceBtn.className = 'btn voice-btn btn-primary';
            document.getElementById('voiceStatus').textContent = 'Ready';
        }
        
        const fallbackOption = document.getElementById('fallbackOption');
        if (this.currentQuestionIndex > 0 && this.isRecording) {
            fallbackOption.style.display = 'block';
        } else {
            fallbackOption.style.display = 'none';
        }
    }

    updateStatus(message) {
        document.getElementById('voiceStatus').textContent = message;
    }

    showFeedback(message, type = 'info') {
        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = `alert alert-${type === 'error' ? 'danger' : type} mt-2`;
        feedbackDiv.textContent = message;
        
        const container = document.getElementById('voiceFeedback');
        if (container) {
            container.innerHTML = '';
            container.appendChild(feedbackDiv);
            
            setTimeout(() => {
                feedbackDiv.remove();
            }, 3000);
        }
    }

    updateAnswerDisplay(field, value) {
        const answerDisplay = document.getElementById('answersDisplay');
        if (!answerDisplay) return;
        
        let existingAnswer = answerDisplay.querySelector(`[data-field="${field}"]`);
        if (!existingAnswer) {
            existingAnswer = document.createElement('div');
            existingAnswer.setAttribute('data-field', field);
            existingAnswer.className = 'answer-item';
            answerDisplay.appendChild(existingAnswer);
        }
        
        const fieldName = field.charAt(0).toUpperCase() + field.slice(1);
        existingAnswer.innerHTML = `<i class="fas fa-check-circle text-success me-2"></i>${fieldName}: <strong>${value}</strong>`;
    }

    showResults(result) {

        const resultsDiv = document.getElementById('voiceResult');
        if (!resultsDiv) return;
        
        const badge = document.getElementById('voiceResultBadge');
        const riskScore = document.getElementById('voiceRiskScore');
        const riskBar = document.getElementById('voiceRiskBar');
        const recommendations = document.getElementById('voiceRecommendations');
        
        resultsDiv.style.display = 'block';
        
        badge.textContent = result.addiction_level;
        badge.className = 'result-badge ' + result.addiction_level.toLowerCase();
        
        const riskPercent = result.risk_score * 100;
        riskScore.textContent = result.risk_score.toFixed(2);
        riskBar.style.width = riskPercent + '%';
        
        if (result.risk_score < 0.33) {
            riskBar.className = 'progress-bar bg-success';
        } else if (result.risk_score < 0.66) {
            riskBar.className = 'progress-bar bg-warning';
        } else {
            riskBar.className = 'progress-bar bg-danger';
        }
        
        recommendations.innerHTML = '';
        result.recommendations.forEach(rec => {
            const div = document.createElement('div');
            div.className = 'alert alert-info mt-2';
            div.innerHTML = `<i class="fas fa-check-circle me-2 text-success"></i>${rec}`;
            recommendations.appendChild(div);
        });
        
        if ('speechSynthesis' in window) {
            const resultMessage = this.language === 'en'
                ? `Your assessment result is ${result.addiction_level}. Risk score is ${result.risk_score.toFixed(2)}.`
                : `Votre résultat d'évaluation est ${result.addiction_level}. Score de risque est ${result.risk_score.toFixed(2)}.`;
            
            const utterance = new SpeechSynthesisUtterance(resultMessage);
            utterance.lang = this.language === 'en' ? 'en-US' : 'fr-FR';
            speechSynthesis.speak(utterance);
        }
        
        resultsDiv.scrollIntoView({ behavior: 'smooth' });
    }
}

let voiceAssessment;

function initVoiceAssessment(language = 'en') {
    voiceAssessment = new VoiceAssessment(language);
    voiceAssessment.init();
    
    updateVoiceUI();
}

function toggleVoiceRecording() {
    if (!voiceAssessment) return;
    
    if (voiceAssessment.isRecording) {
        voiceAssessment.stopAssessment();
    } else {
        voiceAssessment.startAssessment();
    }
    
    updateVoiceUI();
}

function useFallbackAssessment() {
    if (!voiceAssessment) return;
    
    const currentQuestion = voiceAssessment.questions[voiceAssessment.currentQuestionIndex];
    const fallbackValue = Math.floor((currentQuestion.min + currentQuestion.max) / 2);
    
    voiceAssessment.answers[currentQuestion.field] = fallbackValue;
    voiceAssessment.updateAnswerDisplay(currentQuestion.field, fallbackValue);
    
    voiceAssessment.showFeedback(`Using estimated value: ${fallbackValue}`, 'warning');
    
    if (voiceAssessment.currentQuestionIndex < voiceAssessment.questions.length - 1) {
        voiceAssessment.currentQuestionIndex++;
        setTimeout(() => {
            voiceAssessment.speakQuestion();
            voiceAssessment.updateUI();
        }, 1000);
    } else {
        setTimeout(() => voiceAssessment.completeAssessment(), 1000);
    }
}

function updateVoiceUI() {
    if (!voiceAssessment) return;
    
    const voiceBtn = document.getElementById('voiceBtn');
    const status = document.getElementById('voiceStatus');
    
    if (voiceAssessment.isRecording) {
        voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
        voiceBtn.className = 'btn voice-btn btn-danger voice-recording';
        status.textContent = 'Listening...';
    } else {
        voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        voiceBtn.className = 'btn voice-btn btn-primary';
        status.textContent = 'Ready';
    }
}


window.VoiceAssessment = VoiceAssessment;
window.initVoiceAssessment = initVoiceAssessment;
window.toggleVoiceRecording = toggleVoiceRecording;
window.useFallbackAssessment = useFallbackAssessment;