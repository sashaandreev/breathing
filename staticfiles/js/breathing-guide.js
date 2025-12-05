// Breathing Guide JavaScript Engine
// Complete implementation for Phase 4.4

// Torso Pulse Controller Class - Removed (torso graphic removed)

// Main Breathing Guide Engine
class BreathingGuideEngine {
    constructor(techniqueData) {
        this.technique = techniqueData;
        
        // Timing parameters
        this.inhale = techniqueData.inhale;
        this.holdStart = techniqueData.hold_start;
        this.exhale = techniqueData.exhale;
        this.holdEnd = techniqueData.hold_end;
        this.cycleDuration = techniqueData.cycle_duration;
        this.totalTimeSeconds = techniqueData.recommended_time_min * 60;
        
        // State
        this.isRunning = false;
        this.isPaused = false;
        this.startTime = null;
        this.pauseStartTime = null;
        this.totalPauseTime = 0;
        this.currentCycle = 0;
        this.cyclesCompleted = 0;
        this.sessionId = null;
        
        // Preferences from Local Storage
        this.soundEnabled = JSON.parse(localStorage.getItem('soundCueEnabled') || 'true');
        this.vibrationEnabled = JSON.parse(localStorage.getItem('vibrationCueEnabled') || 'true');
        
        // Audio objects
        this.audioFiles = {
            phaseInhale: null,
            phaseExhale: null,
            phaseHold: null,
            counts: {}
        };
        this.phaseCueDuration = 0; // Measured at runtime
        this.audioLoaded = false;
        this.lastCountPlayed = {}; // Track last count played per phase
        
        // Animation
        this.animationFrameId = null;
        this.lastUpdateTime = null;
        
        // DOM elements
        this.balloon = document.getElementById('breathingBalloon');
        this.progressBar = document.getElementById('progressBar');
        this.progressTime = document.getElementById('progressTime');
        this.phaseIndicator = document.getElementById('phaseIndicator');
        this.countdownNumber = document.getElementById('countdownNumber');
        this.pauseButton = document.getElementById('pauseButton');
        this.cancelButton = document.getElementById('cancelButton');
        this.soundStatus = document.getElementById('soundStatus');
        this.vibrationStatus = document.getElementById('vibrationStatus');
        
        // Phase names in Russian
        this.phaseNames = {
            'inhale': 'Вдох',
            'hold_start': 'Задержка',
            'exhale': 'Выдох',
            'hold_end': 'Задержка'
        };
        
        // Number names in Russian (1-10)
        this.numberNames = ['', 'Один', 'Два', 'Три', 'Четыре', 'Пять', 'Шесть', 'Семь', 'Восемь', 'Девять', 'Десять'];
        
        this.init();
    }
    
    init() {
        // Update status icons
        if (this.soundStatus) {
            if (this.soundEnabled) {
                this.soundStatus.classList.add('active');
            }
        }
        if (this.vibrationStatus) {
            if (this.vibrationEnabled) {
                this.vibrationStatus.classList.add('active');
            }
        }
        
        // Set up button handlers
        if (this.pauseButton) {
            this.pauseButton.addEventListener('click', () => this.togglePause());
        }
        if (this.cancelButton) {
            this.cancelButton.addEventListener('click', () => this.cancel());
        }
        
        // Page Visibility API
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && this.isRunning && !this.isPaused) {
                this.pause();
            } else if (!document.hidden && this.isPaused) {
                // Don't auto-resume, user must click resume button
            }
        });
        
        // Start the session
        this.startSession();
    }
    
    async startSession() {
        // Create session record
        await this.createSession();
        
        // Initialize progress bar to 100%
        if (this.progressBar) {
            this.progressBar.style.width = '100%';
        }
        
        // Load audio files
        if (this.soundEnabled) {
            await this.loadAudio();
        }
        
        // Start animation
        this.isRunning = true;
        this.startTime = Date.now();
        this.lastUpdateTime = this.startTime;
        
        // Initialize balloon to starting size (10% - small, ready to grow on inhale)
        if (this.balloon) {
            const viewportWidth = window.innerWidth || 420;
            const startSizePx = Math.max(40, Math.min(350, viewportWidth * 0.10));
            this.balloon.style.width = `${startSizePx}px`;
            this.balloon.style.height = `${startSizePx}px`;
        }
        
        // Start animation loop
        console.log('Starting breathing animation...');
        this.animate();
    }
    
    async createSession() {
        try {
            const response = await fetch('/breathe/api/session/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    action: 'start',
                    technique_id: this.technique.id,
                    sound_enabled: this.soundEnabled,
                    vibration_enabled: this.vibrationEnabled
                })
            });
            
            const data = await response.json();
            if (data.success) {
                this.sessionId = data.session_id;
            }
        } catch (error) {
            console.error('Error creating session:', error);
        }
    }
    
    async loadAudio() {
        const audioBasePath = '/static/audio/ru/';
        
        // Load phase cues
        this.audioFiles.phaseInhale = new Audio(`${audioBasePath}phase_inhale.mp3`);
        this.audioFiles.phaseExhale = new Audio(`${audioBasePath}phase_exhale.mp3`);
        this.audioFiles.phaseHold = new Audio(`${audioBasePath}phase_hold.mp3`);
        
        // Measure phase cue duration (use inhale as reference)
        return new Promise((resolve) => {
            this.audioFiles.phaseInhale.addEventListener('loadedmetadata', () => {
                this.phaseCueDuration = this.audioFiles.phaseInhale.duration * 1000; // Convert to ms
            });
            
            // Load number counts (1-10)
            for (let i = 1; i <= 10; i++) {
                this.audioFiles.counts[i] = new Audio(`${audioBasePath}count_${i}.mp3`);
                this.audioFiles.counts[i].addEventListener('error', () => {
                    // Handle missing files gracefully
                    console.warn(`Audio file count_${i}.mp3 not found`);
                });
            }
            
            // Set a timeout to resolve even if audio doesn't load
            setTimeout(() => {
                this.audioLoaded = true;
                resolve();
            }, 500);
        });
    }
    
    animate() {
        if (!this.isRunning || this.isPaused) {
            if (this.isPaused) {
                return; // Don't continue animation if paused
            }
            // If not running, try to restart
            if (!this.isRunning) {
                return;
            }
        }
        
        const now = Date.now();
        const elapsed = (now - this.startTime - this.totalPauseTime) / 1000; // seconds
        
        // Check if session time has expired
        if (elapsed >= this.totalTimeSeconds) {
            // Allow current cycle to finish
            const cycleElapsed = elapsed % this.cycleDuration;
            if (cycleElapsed >= this.cycleDuration - this.holdEnd) {
                // Current cycle is finishing, complete session
                this.complete();
                return;
            }
        }
        
        // Calculate current phase and phase progress
        const cycleElapsed = elapsed % this.cycleDuration;
        let phase, phaseElapsed, phaseDuration, phaseProgress;
        
        if (cycleElapsed < this.inhale) {
            phase = 'inhale';
            phaseElapsed = cycleElapsed;
            phaseDuration = this.inhale;
        } else if (cycleElapsed < this.inhale + this.holdStart) {
            phase = 'hold_start';
            phaseElapsed = cycleElapsed - this.inhale;
            phaseDuration = this.holdStart;
        } else if (cycleElapsed < this.inhale + this.holdStart + this.exhale) {
            phase = 'exhale';
            phaseElapsed = cycleElapsed - this.inhale - this.holdStart;
            phaseDuration = this.exhale;
        } else {
            phase = 'hold_end';
            phaseElapsed = cycleElapsed - this.inhale - this.holdStart - this.exhale;
            phaseDuration = this.holdEnd;
        }
        
        phaseProgress = phaseElapsed / phaseDuration;
        
        // Update cycle count
        const newCycle = Math.floor(elapsed / this.cycleDuration);
        if (newCycle > this.currentCycle) {
            this.currentCycle = newCycle;
            this.cyclesCompleted = newCycle;
            this.updateSessionCycles();
        }
        
        // Update UI (with error handling)
        try {
            this.updateBalloon(phase, phaseProgress);
            this.updateProgressBar(elapsed);
            this.updatePhaseIndicator(phase, phaseElapsed, phaseDuration);
            this.handleAudio(phase, phaseElapsed, phaseDuration);
            this.handleHaptic(phase, phaseElapsed);
        } catch (error) {
            console.error('Error updating UI:', error);
        }
        
        // Continue animation
        if (this.isRunning && !this.isPaused) {
            this.animationFrameId = requestAnimationFrame(() => this.animate());
        }
    }
    
    updateBalloon(phase, progress) {
        if (!this.balloon) {
            console.warn('Balloon element not found');
            return;
        }
        
        // Much more dramatic size change: from 90% (full) to 10% (almost zero)
        let sizePercent;
        if (phase === 'inhale') {
            // Inhale: grow from 10% to 90%
            sizePercent = 10 + (progress * 80); // 10% to 90%
        } else if (phase === 'hold_start') {
            // Hold: maintain 90%
            sizePercent = 90;
        } else if (phase === 'exhale') {
            // Exhale: shrink from 90% to 10%
            sizePercent = 90 - (progress * 80); // 90% to 10%
        } else {
            // Hold end: maintain 10%
            sizePercent = 10;
        }
        
        // Ensure size is within bounds
        sizePercent = Math.max(10, Math.min(90, sizePercent));
        
        // Calculate pixel size based on viewport width
        const viewportWidth = window.innerWidth || 420;
        const minSizePx = Math.max(40, (viewportWidth * 0.10)); // 10% minimum (40px floor)
        const maxSizePx = Math.min(viewportWidth * 0.90, 350); // 90% maximum, capped at 350px
        const currentSizePx = minSizePx + ((maxSizePx - minSizePx) * ((sizePercent - 10) / 80));
        
        // Apply size directly without CSS transition for smooth animation
        this.balloon.style.width = `${currentSizePx}px`;
        this.balloon.style.height = `${currentSizePx}px`;
        this.balloon.style.maxWidth = '350px';
        this.balloon.style.maxHeight = '350px';
        this.balloon.style.minWidth = '40px';
        this.balloon.style.minHeight = '40px';
    }
    
    updateProgressBar(elapsed) {
        if (!this.progressBar || !this.progressTime) return;
        
        const remaining = Math.max(0, this.totalTimeSeconds - elapsed);
        const progress = Math.min(100, (remaining / this.totalTimeSeconds) * 100); // Reversed: start at 100%, go to 0%
        
        this.progressBar.style.width = `${progress}%`;
        
        const minutes = Math.floor(remaining / 60);
        const seconds = Math.floor(remaining % 60);
        this.progressTime.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }
    
    updatePhaseIndicator(phase, phaseElapsed, phaseDuration) {
        if (!this.phaseIndicator || !this.countdownNumber) return;
        
        this.phaseIndicator.textContent = this.phaseNames[phase] || phase;
        
        const count = Math.ceil(phaseDuration - phaseElapsed);
        if (count > 0 && count <= 10) {
            this.countdownNumber.textContent = this.numberNames[count] || count;
        } else {
            this.countdownNumber.textContent = '';
        }
    }
    
    handleAudio(phase, phaseElapsed, phaseDuration) {
        if (!this.soundEnabled || !this.audioLoaded) return;
        
        const phaseElapsedMs = phaseElapsed * 1000;
        const phaseDurationMs = phaseDuration * 1000;
        
        // Play phase cue at start (0s)
        if (phaseElapsedMs < 100) { // Within first 100ms
            let phaseAudio = null;
            if (phase === 'inhale') {
                phaseAudio = this.audioFiles.phaseInhale;
            } else if (phase === 'exhale') {
                phaseAudio = this.audioFiles.phaseExhale;
            } else if (phase === 'hold_start' || phase === 'hold_end') {
                phaseAudio = this.audioFiles.phaseHold;
            }
            
            if (phaseAudio) {
                phaseAudio.currentTime = 0;
                phaseAudio.play().catch(e => console.warn('Audio play failed:', e));
            }
            
            // Reset count tracking for new phase
            this.lastCountPlayed[phase] = -1;
        }
        
        // Play number counts every second (after phase cue)
        // Count represents seconds remaining: for 4s phase, play 4, 3, 2, 1
        const countDelay = this.phaseCueDuration || 500; // Wait for phase cue to finish
        const countTime = phaseElapsedMs - countDelay;
        
        if (countTime >= 0) {
            const secondsElapsed = Math.floor(countTime / 1000);
            const count = Math.ceil(phaseDuration - phaseElapsed); // Countdown number
            
            // Play count audio every second (after phase cue delay)
            if (count > 0 && count <= 10 && secondsElapsed >= 0) {
                // Only play if we haven't played this count for this phase
                if (this.lastCountPlayed[phase] !== count) {
                    this.lastCountPlayed[phase] = count;
                    const countAudio = this.audioFiles.counts[count];
                    if (countAudio && countAudio.readyState >= 2) {
                        countAudio.currentTime = 0;
                        countAudio.play().catch(e => console.warn('Count audio play failed:', e));
                    }
                }
            }
        }
    }
    
    handleHaptic(phase, phaseElapsed) {
        if (!this.vibrationEnabled || !navigator.vibrate) return;
        
        // Vibrate at phase start (within first 100ms)
        if (phaseElapsed < 0.1) {
            navigator.vibrate(100);
        }
    }
    
    togglePause() {
        if (this.isPaused) {
            this.resume();
        } else {
            this.pause();
        }
    }
    
    pause() {
        if (!this.isRunning || this.isPaused) return;
        
        this.isPaused = true;
        this.pauseStartTime = Date.now();
        
        if (this.pauseButton) {
            const label = this.pauseButton.querySelector('.button-label');
            if (label) label.textContent = 'Продолжить';
            const icon = this.pauseButton.querySelector('.button-icon');
            if (icon) icon.textContent = '▶️';
        }
        
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
        }
    }
    
    resume() {
        if (!this.isPaused) return;
        
        this.isPaused = false;
        if (this.pauseStartTime) {
            this.totalPauseTime += Date.now() - this.pauseStartTime;
            this.pauseStartTime = null;
        }
        
        if (this.pauseButton) {
            const label = this.pauseButton.querySelector('.button-label');
            if (label) label.textContent = 'Пауза';
            const icon = this.pauseButton.querySelector('.button-icon');
            if (icon) icon.textContent = '⏸️';
        }
        
        this.lastUpdateTime = Date.now();
        this.animate();
    }
    
    async cancel() {
        if (confirm('Вы уверены, что хотите отменить сессию?')) {
            this.isRunning = false;
            this.isPaused = false;
            
            if (this.animationFrameId) {
                cancelAnimationFrame(this.animationFrameId);
            }
            
            // Update session as cancelled
            if (this.sessionId) {
                await this.updateSession('cancel');
            }
            
            // Redirect to categories
            window.location.href = '/breathe/';
        }
    }
    
    async complete() {
        this.isRunning = false;
        this.isPaused = false;
        
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
        }
        
        // Update session as completed
        if (this.sessionId) {
            await this.updateSession('complete');
        }
        
        // Show success message
        alert('Сессия завершена! Вы молодец.');
        
        // Redirect to categories after 2 seconds
        setTimeout(() => {
            window.location.href = '/breathe/';
        }, 2000);
    }
    
    async updateSessionCycles() {
        if (!this.sessionId) return;
        
        try {
            await fetch('/breathe/api/session/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    action: 'update',
                    session_id: this.sessionId,
                    cycles_completed: this.cyclesCompleted
                })
            });
        } catch (error) {
            console.error('Error updating session cycles:', error);
        }
    }
    
    async updateSession(action) {
        if (!this.sessionId) return;
        
        try {
            await fetch('/breathe/api/session/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    action: action,
                    session_id: this.sessionId,
                    cycles_completed: this.cyclesCompleted
                })
            });
        } catch (error) {
            console.error(`Error ${action}ing session:`, error);
        }
    }
    
    getCSRFToken() {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput) return csrfInput.value;
        
        // Fallback to cookie
        const name = 'csrftoken';
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
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (window.techniqueData) {
        const engine = new BreathingGuideEngine(window.techniqueData);
        // Store engine globally for debugging
        window.breathingEngine = engine;
    } else {
        console.error('Technique data not found');
    }
});
