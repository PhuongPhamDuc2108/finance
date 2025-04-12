// Voice Recognition Script
document.addEventListener('DOMContentLoaded', function() {
    const micButton = document.getElementById('mic-button');
    const voiceResult = document.getElementById('voice-result');
    // Load Font Awesome
    const fa = document.createElement('link');
    fa.rel = 'stylesheet';
    fa.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css';
    document.head.appendChild(fa);

    // Check browser support
    if (!('webkitSpeechRecognition' in window)) {
        micButton.disabled = true;
        micButton.title = 'Trình duyệt không hỗ trợ nhận dạng giọng nói';
        voiceResult.style.display = 'block';
        voiceResult.textContent = 'Trình duyệt của bạn không hỗ trợ nhận dạng giọng nói. Vui lòng sử dụng Chrome hoặc Edge.';
        return;
    }

    let recognition = null; // Will be initialized on first click
    
    function initRecognition() {
        console.log('Initializing voice recognition...');
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'vi-VN';
        
        // Setup event handlers
        recognition.onstart = function() {
            console.log('Recording started');
            if (micButton.classList.contains('recording')) {
                voiceResult.textContent = 'Đang nghe... Hãy nói lệnh của bạn';
            }
        };
        
        recognition.onend = function() {
            console.log('Recording ended');
            if (micButton.classList.contains('recording')) {
                micButton.classList.remove('recording');
                micButton.innerHTML = '<i class="fas fa-microphone"></i>';
                micButton.title = 'Nhấn để bắt đầu ghi âm';
            }
            // Clean up
            recognition = null;
        };
        
        recognition.onerror = function(event) {
            console.error('Recording error:', event.error);
            // Error handling remains the same
        };
    }

    // Handle mic button click
    micButton.addEventListener('click', function() {
        if (micButton.classList.contains('recording')) {
            console.log('Stopping recording...');
            if (recognition) {
                recognition.abort();
                recognition.stop();
            }
            voiceResult.textContent = 'Đã dừng ghi âm. Đang xử lý...';
            return;
        }

        try {
            if (!recognition) {
                initRecognition();
            }
            console.log('Starting recording...');
            recognition.start();
            micButton.classList.add('recording');
            micButton.innerHTML = '<i class="fas fa-microphone-slash"></i>';
            micButton.title = 'Nhấn để dừng ghi âm';
            voiceResult.style.display = 'block';
            voiceResult.textContent = 'Đang ghi âm... Nói "Thêm Lương, 1000000" hoặc lệnh khác';
        } catch (error) {
            voiceResult.textContent = 'Lỗi khi bắt đầu ghi âm: ' + error.message;
            micButton.classList.remove('recording');
            micButton.innerHTML = '<i class="fas fa-microphone"></i>';
            micButton.title = 'Nhấn để bắt đầu ghi âm';
        }
    });

    // Set initial tooltip
    micButton.title = 'Nhấn để bắt đầu ghi âm';

    // Recognition event handlers
    recognition.onstart = function() {
        // Only update if we're in recording state (button was clicked)
        if (micButton.classList.contains('recording')) {
            voiceResult.textContent = 'Đang nghe... Hãy nói lệnh của bạn';
        }
    };

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        voiceResult.textContent = `Bạn nói: ${transcript}`;
        processVoiceCommand(transcript);
    };

    recognition.onerror = function(event) {
        let errorMessage = 'Lỗi: ';
        switch(event.error) {
            case 'no-speech':
                errorMessage += 'Không phát hiện giọng nói';
                break;
            case 'audio-capture':
                errorMessage += 'Không thể truy cập microphone';
                break;
            case 'not-allowed':
                errorMessage += 'Microphone bị chặn. Vui lòng cho phép truy cập microphone.';
                break;
            default:
                errorMessage += event.error;
        }
        voiceResult.textContent = errorMessage;
        micButton.classList.remove('recording');
        micButton.innerHTML = '<i class="fas fa-microphone"></i>';
    };

    recognition.onend = function() {
        if (micButton.classList.contains('recording')) {
            micButton.classList.remove('recording');
            micButton.innerHTML = '<i class="fas fa-microphone"></i>';
        }
    };

    async function processVoiceCommand(command) {
        command = command.toLowerCase();
        
        // First handle form filling if on add income page
        if (window.location.pathname === "{% url 'add_income' %}") {
            const incomeMatch = command.match(/(.+?)\s+(\d+)/);
            if (incomeMatch) {
                const type = incomeMatch[1].trim();
                const amount = parseInt(incomeMatch[2].replace(/\D/g, ''));
                
                document.getElementById('id_description').value = type;
                document.getElementById('id_amount').value = amount;
                document.getElementById('id_date').value = new Date().toISOString().split('T')[0];
                
                setTimeout(() => {
                    document.querySelector('form').submit();
                    setTimeout(() => {
                        window.location.href = "{% url 'financial_report' %}";
                    }, 1000);
                }, 500);
                
                voiceResult.textContent = `Đã thêm ${type} ${amount.toLocaleString()}đ và chuyển trang...`;
                return;
            }
        }
        
        // For all other commands, use the backend processor
        try {
            voiceResult.textContent = 'Đang xử lý lệnh...';
            
            const response = await fetch("{% url 'process_voice_command' %}", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({command: command})
            });
            
            const data = await response.json();
            
            if (data.action === "navigate") {
                voiceResult.textContent = `Đang chuyển đến: ${data.url}`;
                setTimeout(() => window.location.href = data.url, 1000);
            } else if (data.response) {
                voiceResult.textContent = `AI: ${data.response}`;
            } else {
                voiceResult.textContent += '\nKhông nhận diện được lệnh. Vui lòng thử lại.';
            }
        } catch (error) {
            console.error('Voice command error:', error);
            voiceResult.textContent = 'Có lỗi xảy ra khi xử lý lệnh. Vui lòng thử lại.';
        }
    }

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
