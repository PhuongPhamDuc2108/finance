document.addEventListener('DOMContentLoaded', function () {
    const micButton = document.getElementById('mic-button');
    const voiceResult = document.getElementById('voice-result');

    const fa = document.createElement('link');
    fa.rel = 'stylesheet';
    fa.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css';
    document.head.appendChild(fa);

    if (!('webkitSpeechRecognition' in window)) {
        micButton.disabled = true;
        micButton.title = 'Trình duyệt không hỗ trợ nhận dạng giọng nói';
        voiceResult.style.display = 'block';
        voiceResult.textContent = 'Trình duyệt của bạn không hỗ trợ nhận dạng giọng nói. Vui lòng sử dụng Chrome hoặc Edge.';
        return;
    }

    let recognition = null;
    let isRecording = false;

    function initRecognition() {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'vi-VN';

        recognition.onstart = function () {
            micButton.classList.add('recording');
            micButton.innerHTML = '<i class="fas fa-microphone-slash"></i>';
            micButton.title = 'Đang ghi âm...';
            voiceResult.style.display = 'block';
            voiceResult.textContent = 'Đang nghe... Hãy nói lệnh của bạn';
        };

        recognition.onend = function () {
            micButton.classList.remove('recording');
            micButton.innerHTML = '<i class="fas fa-microphone"></i>';
            micButton.title = 'Nhấn phím "m" để ghi âm';
            recognition = null;
            isRecording = false;
        };

        recognition.onerror = function (event) {
            console.error('Recording error:', event.error);
        };

        recognition.onresult = function (event) {
            const transcript = event.results[0][0].transcript;
            voiceResult.textContent = `Bạn nói: ${transcript}`;
            processVoiceCommand(transcript);
        };
    }

    function handleRecordingToggle() {
        if (isRecording) {
            if (recognition) {
                recognition.stop();
                voiceResult.textContent = 'Đã dừng ghi âm. Đang xử lý...';
            }
        } else {
            initRecognition();
            try {
                recognition.start();
                isRecording = true;
            } catch (error) {
                console.error('Start error:', error);
            }
        }
    }

    // Nhấn phím "m" để bật/tắt thu âm
    document.addEventListener('keydown', function (event) {
        if (event.key === 'm' || event.key === 'M') {
            handleRecordingToggle();
        }
    });

    micButton.title = 'Nhấn phím "m" để ghi âm';

    async function processVoiceCommand(command) {
        command = command.toLowerCase();

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

        try {
            voiceResult.textContent = 'Đang xử lý lệnh...';
            const response = await fetch("{% url 'process_voice_command' %}", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ command })
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
