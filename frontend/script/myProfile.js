document.addEventListener('DOMContentLoaded', function () {

    /* ============================================================
       PROFILE — Edit / Cancel
       ============================================================ */
    const showInfo      = document.getElementById('display-mode');
    const editInfoFORM  = document.getElementById('edit-mode');
    const editButton    = document.getElementById('edit-profile-btn');
    const cancelEditBtn = document.getElementById('cancel-edit');
    const actionButtons = document.getElementById('action-buttons');

    if (!showInfo || !editInfoFORM || !editButton) {
        console.error('Required elements not found:', {
            showInfo:     !!showInfo,
            editInfoFORM: !!editInfoFORM,
            editButton:   !!editButton
        });
        return;
    }

    editButton.addEventListener('click', () => {
        showInfo.style.display      = 'none';
        actionButtons.style.display = 'none';
        editInfoFORM.style.display  = 'flex';
    });

    cancelEditBtn.addEventListener('click', () => {
        editInfoFORM.style.display  = 'none';
        showInfo.style.display      = 'grid';
        actionButtons.style.display = 'flex';
    });

    // Profile form — fetch submit
    editInfoFORM.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(editInfoFORM);

        fetch('/profile', {
            method: 'POST',
            body: formData,
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showInfo.style.display      = 'grid';
                editInfoFORM.style.display  = 'none';
                actionButtons.style.display = 'flex';
                window.location.reload();
            } else {
                alert(data.message || 'Failed to update profile');
            }
        })
        .catch(() => alert('Failed to update profile. Please try again.'));
    });


    /* ============================================================
       PASSWORD MODAL — Open / Close
       ============================================================ */
    document.getElementById('change-password-btn').addEventListener('click', () => {
        document.getElementById('password-modal').classList.add('active');
        document.body.style.overflow = 'hidden';
    });

    // Close on backdrop click
    document.getElementById('password-modal').addEventListener('click', function (e) {
        if (e.target === this) closePasswordModal();
    });

    // Close on Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closePasswordModal();
    });

    // Password form — fetch submit
    document.getElementById('change-password-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const btn = document.querySelector('#pw-step-2 .pw-btn-primary');

        btn.classList.add('loading');
        btn.textContent = 'Updating…';

        fetch('/change_password', {
            method: 'POST',
            body: formData,
        })
        .then(res => res.json())
        .then(data => {
            btn.classList.remove('loading');
            btn.textContent = 'Update Password';

            if (data.success) {
                document.getElementById('pw-step-2').classList.remove('active');
                document.getElementById('dot-2').className          = 'pw-step-dot done';
                document.getElementById('pw-card-title').textContent = 'All Done';
                document.getElementById('pw-card-sub').textContent   = '';
                document.getElementById('pw-success-view').classList.add('active');
            } else {
                // Wrong current password → go back to step 1 and show error there
                if (data.message && data.message.toLowerCase().includes('unauthorized')) {
                    const input = document.getElementById('current-password');
                    const err   = document.getElementById('err-current');
                    err.textContent   = 'Incorrect password. Please try again.';
                    err.style.display = 'block';
                    input.classList.add('pw-error');
                    pwGoBack();
                } else {
                    const err = document.getElementById('err-confirm');
                    err.textContent   = data.message || 'Something went wrong. Try again.';
                    err.style.display = 'block';
                }
            }
        })
        .catch(() => {
            btn.classList.remove('loading');
            btn.textContent = 'Update Password';
            const err = document.getElementById('err-confirm');
            err.textContent   = 'Network error. Please try again.';
            err.style.display = 'block';
        });
    });

}); // end DOMContentLoaded


/* ============================================================
   PASSWORD MODAL — Close + Reset
   ============================================================ */
function closePasswordModal() {
    document.getElementById('password-modal').classList.remove('active');
    document.body.style.overflow = '';
    pwResetModal();
}

function pwResetModal() {
    document.getElementById('pw-step-1').classList.add('active');
    document.getElementById('pw-step-2').classList.remove('active');
    document.getElementById('pw-success-view').classList.remove('active');

    document.getElementById('dot-1').className = 'pw-step-dot active';
    document.getElementById('dot-2').className = 'pw-step-dot';

    document.getElementById('pw-card-title').textContent = 'Verify Identity';
    document.getElementById('pw-card-sub').textContent   = 'Enter your current password to continue';

    document.getElementById('current-password').value = '';
    document.getElementById('new-password').value     = '';
    document.getElementById('confirm-password').value = '';

    // Reset errors (text too, in case server overwrote them)
    document.getElementById('err-current').style.display = 'none';
    document.getElementById('err-confirm').style.display = 'none';
    document.getElementById('err-current').textContent   = 'Please enter your current password';
    document.getElementById('err-confirm').textContent   = 'Passwords do not match';

    document.getElementById('current-password').classList.remove('pw-error');
    document.getElementById('new-password').classList.remove('pw-error');
    document.getElementById('confirm-password').classList.remove('pw-error');

    document.getElementById('pw-strength-fill').style.width      = '0%';
    document.getElementById('pw-strength-fill').style.background = 'transparent';
    document.getElementById('pw-strength-label').textContent     = '';

    const submitBtn = document.querySelector('#pw-step-2 .pw-btn-primary');
    submitBtn.classList.remove('loading');
    submitBtn.textContent = 'Update Password';
}


/* ============================================================
   PASSWORD MODAL — Step navigation
   ============================================================ */
function pwGoToStep2() {
    const input = document.getElementById('current-password');
    const err   = document.getElementById('err-current');

    if (!input.value.trim()) {
        input.classList.add('pw-error');
        err.style.display = 'block';
        input.focus();
        return;
    }

    input.classList.remove('pw-error');
    err.style.display = 'none';

    document.getElementById('pw-step-1').classList.remove('active');
    document.getElementById('pw-step-2').classList.add('active');
    document.getElementById('dot-1').className = 'pw-step-dot done';
    document.getElementById('dot-2').className = 'pw-step-dot active';
    document.getElementById('pw-card-title').textContent = 'New Password';
    document.getElementById('pw-card-sub').textContent   = 'Choose a strong, unique password';
    document.getElementById('new-password').focus();
}

function pwGoBack() {
    document.getElementById('pw-step-2').classList.remove('active');
    document.getElementById('pw-step-1').classList.add('active');
    document.getElementById('dot-2').className = 'pw-step-dot';
    document.getElementById('dot-1').className = 'pw-step-dot active';
    document.getElementById('pw-card-title').textContent = 'Verify Identity';
    document.getElementById('pw-card-sub').textContent   = 'Enter your current password to continue';
}


/* ============================================================
   PASSWORD MODAL — Strength meter
   ============================================================ */
function pwCheckStrength(val) {
    const fill  = document.getElementById('pw-strength-fill');
    const label = document.getElementById('pw-strength-label');

    let score = 0;
    if (val.length >= 8)           score++;
    if (val.length >= 12)          score++;
    if (/[A-Z]/.test(val))        score++;
    if (/[0-9]/.test(val))        score++;
    if (/[^A-Za-z0-9]/.test(val)) score++;

    const levels = [
        { pct: '0%',   color: 'transparent',      text: '' },
        { pct: '20%',  color: 'var(--pw-error)',   text: 'Weak' },
        { pct: '40%',  color: 'var(--pw-error)',   text: 'Fair' },
        { pct: '60%',  color: 'var(--pw-accent)',  text: 'Moderate' },
        { pct: '80%',  color: 'var(--pw-accent)',  text: 'Strong' },
        { pct: '100%', color: 'var(--pw-success)', text: 'Excellent' },
    ];

    const lvl = val.length === 0 ? 0 : Math.max(1, score);
    fill.style.width      = levels[lvl].pct;
    fill.style.background = levels[lvl].color;
    label.textContent     = levels[lvl].text;
    label.style.color     = levels[lvl].color;
}


/* ============================================================
   PASSWORD MODAL — Show / Hide toggle
   ============================================================ */
function pwToggleVis(inputId, el) {
    const input  = document.getElementById(inputId);
    const hidden = input.type === 'password';
    input.type    = hidden ? 'text' : 'password';
    el.textContent = hidden ? 'hide' : 'show';
}


/* ============================================================
   PASSWORD MODAL — Client-side validation then submit
   ============================================================ */
function pwSubmitForm() {
    const newPw   = document.getElementById('new-password');
    const confPw  = document.getElementById('confirm-password');
    const errConf = document.getElementById('err-confirm');
    let valid = true;

    if (!newPw.value || newPw.value.length < 8) {
        newPw.classList.add('pw-error');
        valid = false;
    } else {
        newPw.classList.remove('pw-error');
    }

    if (!confPw.value || newPw.value !== confPw.value) {
        confPw.classList.add('pw-error');
        errConf.textContent   = 'Passwords do not match';
        errConf.style.display = 'block';
        valid = false;
    } else {
        confPw.classList.remove('pw-error');
        errConf.style.display = 'none';
    }

    if (!valid) return;

    // Fire the form submit event — handled by the listener in DOMContentLoaded
    document.getElementById('change-password-form').requestSubmit();
} 
