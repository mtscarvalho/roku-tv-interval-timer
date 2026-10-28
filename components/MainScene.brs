sub init()
    m.appRoot = m.top.findNode("appRoot")
    m.configView = m.top.findNode("configView")
    m.timerView = m.top.findNode("timerView")
    m.finishedView = m.top.findNode("finishedView")
    m.selection = m.top.findNode("selection")
    m.startButton = m.top.findNode("startButton")
    m.startLabel = m.top.findNode("startLabel")
    m.startActiveAnimation = m.top.findNode("startActiveAnimation")
    m.startInactiveAnimation = m.top.findNode("startInactiveAnimation")
    m.workValue = m.top.findNode("workValue")
    m.restValue = m.top.findNode("restValue")
    m.roundsValue = m.top.findNode("roundsValue")
    m.phaseLabel = m.top.findNode("phaseLabel")
    m.roundLabel = m.top.findNode("roundLabel")
    m.clockLabel = m.top.findNode("clockLabel")
    m.clockNormalFont = m.top.findNode("poppinsSemiBold160")
    m.clockCountdownFont = m.top.findNode("poppinsSemiBold220")
    m.progressBar = m.top.findNode("progressBar")
    m.statusLabel = m.top.findNode("statusLabel")
    m.summaryLabel = m.top.findNode("summaryLabel")
    m.tickTimer = m.top.findNode("tickTimer")
    m.beepAudio = m.top.findNode("beepAudio")
    m.completeAudio = m.top.findNode("completeAudio")

    beepContent = CreateObject("roSGNode", "ContentNode")
    beepContent.url = "pkg:/audio/countdown.wav"
    m.beepAudio.content = beepContent
    completeContent = CreateObject("roSGNode", "ContentNode")
    completeContent.url = "pkg:/audio/complete.wav"
    m.completeAudio.content = completeContent
    m.tickTimer.observeField("fire", "onTimerTick")

    m.workSeconds = 30
    m.restSeconds = 15
    m.totalRounds = 5
    m.selectedRow = 0
    m.startWasSelected = false
    m.mode = "config"
    m.phase = ""
    m.currentRound = 1
    m.isPaused = false
    updateConfigView()
end sub

function onKeyEvent(key as String, press as Boolean) as Boolean
    if not press then return false
    if m.mode = "config"
        return handleConfigKey(key)
    else if m.mode = "running"
        if key = "OK"
            togglePause()
            return true
        else if key = "back"
            returnToConfig()
            return true
        end if
    else if m.mode = "finished"
        if key = "OK" or key = "back"
            returnToConfig()
            return true
        end if
    end if
    return false
end function

function handleConfigKey(key as String) as Boolean
    if key = "up"
        m.selectedRow = m.selectedRow - 1
        if m.selectedRow < 0 then m.selectedRow = 3
        updateSelection()
        return true
    else if key = "down"
        m.selectedRow = m.selectedRow + 1
        if m.selectedRow > 3 then m.selectedRow = 0
        updateSelection()
        return true
    else if key = "left"
        changeSelectedValue(-1)
        return true
    else if key = "right"
        changeSelectedValue(1)
        return true
    else if key = "OK"
        if m.selectedRow = 3
            startWorkout()
        else
            changeSelectedValue(1)
        end if
        return true
    end if
    return false
end function

sub changeSelectedValue(direction as Integer)
    if m.selectedRow = 0
        m.workSeconds = clamp(m.workSeconds + (direction * 15), 15, 3600)
    else if m.selectedRow = 1
        m.restSeconds = clamp(m.restSeconds + (direction * 15), 0, 1800)
    else if m.selectedRow = 2
        m.totalRounds = clamp(m.totalRounds + direction, 1, 99)
    end if
    updateConfigView()
end sub

function clamp(value as Integer, minimum as Integer, maximum as Integer) as Integer
    if value < minimum then return minimum
    if value > maximum then return maximum
    return value
end function

sub updateConfigView()
    m.workValue.text = formatTime(m.workSeconds)
    m.restValue.text = formatTime(m.restSeconds)
    m.roundsValue.text = m.totalRounds.toStr()
    updateSelection()
end sub

sub updateSelection()
    rowY = 190 + (m.selectedRow * 90)
    m.selection.translation = [67, rowY]
    if m.selectedRow = 3
        m.selection.visible = false
        if not m.startWasSelected
            m.startInactiveAnimation.control = "stop"
            m.startActiveAnimation.control = "start"
        end if
        m.startWasSelected = true
    else
        m.selection.visible = true
        if m.startWasSelected
            m.startActiveAnimation.control = "stop"
            m.startInactiveAnimation.control = "start"
        end if
        m.startWasSelected = false
    end if
end sub

sub startWorkout()
    m.mode = "running"
    m.currentRound = 1
    m.isPaused = false
    m.configView.visible = false
    m.finishedView.visible = false
    m.timerView.visible = true
    startPhase("prepare", 3)
end sub

sub startPhase(phase as String, seconds as Integer)
    m.phase = phase
    m.phaseDuration = seconds
    m.remainingSeconds = seconds
    m.lastSoundSecond = -1
    updateTimerView()
    if phase = "prepare"
        playBeep()
        m.lastSoundSecond = seconds
    end if
    m.tickTimer.control = "start"
end sub

sub onTimerTick()
    if m.mode <> "running" or m.isPaused then return
    m.remainingSeconds = m.remainingSeconds - 1
    if m.remainingSeconds <= 0
        advancePhase()
        return
    end if
    if m.remainingSeconds <= 3 and m.remainingSeconds <> m.lastSoundSecond
        playBeep()
        m.lastSoundSecond = m.remainingSeconds
    end if
    updateTimerView()
end sub

sub advancePhase()
    if m.phase = "prepare"
        startPhase("work", m.workSeconds)
    else if m.phase = "work"
        playComplete()
        if m.currentRound >= m.totalRounds
            finishWorkout()
        else if m.restSeconds > 0
            startPhase("rest", m.restSeconds)
        else
            m.currentRound = m.currentRound + 1
            startPhase("prepare", 3)
        end if
    else if m.phase = "rest"
        m.currentRound = m.currentRound + 1
        startPhase("prepare", 3)
    end if
end sub

sub updateTimerView()
    if m.phase = "prepare"
        m.phaseLabel.visible = true
        m.phaseLabel.text = "PREPARE-SE"
        m.roundLabel.translation = [80, 105]
        m.clockLabel.text = m.remainingSeconds.toStr()
        m.clockLabel.font = m.clockCountdownFont
        m.clockLabel.translation = [80, 140]
        m.clockLabel.height = 270
        m.progressBar.color = "0xde0b37ff"
    else if m.phase = "work"
        m.phaseLabel.visible = false
        m.phaseLabel.text = ""
        m.roundLabel.translation = [80, 95]
        m.clockLabel.text = formatTime(m.remainingSeconds)
        m.clockLabel.font = m.clockNormalFont
        m.clockLabel.translation = [80, 140]
        m.clockLabel.height = 240
        m.progressBar.color = "0xde0b37ff"
    else
        m.phaseLabel.visible = true
        m.phaseLabel.text = "INTERVALO"
        m.roundLabel.translation = [80, 105]
        m.clockLabel.text = formatTime(m.remainingSeconds)
        m.clockLabel.font = m.clockNormalFont
        m.clockLabel.translation = [80, 140]
        m.clockLabel.height = 240
        m.progressBar.color = "0xde0b37ff"
    end if

    m.roundLabel.text = "RODADA " + m.currentRound.toStr() + " DE " + m.totalRounds.toStr()
    progress = 1.0
    if m.phaseDuration > 0 then progress = m.remainingSeconds / m.phaseDuration
    m.progressBar.width = Int(934 * progress)
    if m.isPaused
        m.statusLabel.text = "PAUSADO — pressione OK para continuar"
    else
        m.statusLabel.text = "OK para pausar"
    end if
end sub

sub togglePause()
    m.isPaused = not m.isPaused
    if m.isPaused
        m.tickTimer.control = "stop"
    else
        m.tickTimer.control = "start"
    end if
    updateTimerView()
end sub

sub finishWorkout()
    m.tickTimer.control = "stop"
    m.mode = "finished"
    m.timerView.visible = false
    m.finishedView.visible = true
    m.summaryLabel.text = m.totalRounds.toStr() + " rodadas de " + formatTime(m.workSeconds) + chr(10) + "Bom trabalho!"
end sub

sub returnToConfig()
    m.tickTimer.control = "stop"
    m.beepAudio.control = "stop"
    m.completeAudio.control = "stop"
    m.mode = "config"
    m.isPaused = false
    m.timerView.visible = false
    m.finishedView.visible = false
    m.configView.visible = true
    updateConfigView()
end sub

sub playBeep()
    m.beepAudio.control = "stop"
    m.beepAudio.control = "play"
end sub

sub playComplete()
    m.completeAudio.control = "stop"
    m.completeAudio.control = "play"
end sub

function formatTime(totalSeconds as Integer) as String
    minutes = Int(totalSeconds / 60)
    seconds = totalSeconds mod 60
    secondsText = seconds.toStr()
    if seconds < 10 then secondsText = "0" + secondsText
    return minutes.toStr() + ":" + secondsText
end function

