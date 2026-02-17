document.addEventListener('DOMContentLoaded', function() {
    const showInfo = document.getElementById("display-mode");
    const editInfoFORM = document.getElementById("edit-mode");
    const editButton = document.getElementById("edit-profile-btn");
    const displayMode    = document.getElementById('display-mode');
    let isEditing = false;

    // Check if elements exist
    if (!showInfo || !editInfoFORM || !editButton) {
        console.error('Required elements not found:', {
            showInfo: !!showInfo,
            editInfoFORM: !!editInfoFORM,
            editButton: !!editButton
        });
        return;
    }

    editButton.addEventListener("click", () => {
        if (!isEditing) {
            // Switch to edit mode
            showInfo.style.display = "none";
            editInfoFORM.style.display = "flex";
            editButton.innerText = "Save changes";
            editButton.style.backgroundColor = "green";
            isEditing = true;
        } else {
            // Trigger form submission
            const submitEvent = new Event('submit', { 
                cancelable: true, 
                bubbles: true 
            });
            editInfoFORM.dispatchEvent(submitEvent);
        }
    });

    // Form submission
    editInfoFORM.addEventListener("submit", (event) => {
        event.preventDefault();
        const formData = new FormData(editInfoFORM);
        
        fetch("/profile", {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            console.log("Success:", data);
            
            if (data.success) {
                // Switch back to display mode
                showInfo.style.display = "grid";
                editInfoFORM.style.display = "none";
                editButton.innerText = "Edit Profile";
                editButton.style.backgroundColor = "";
                isEditing = false;
                
                alert("Profile updated successfully!");
                window.location.reload();
            } else {
                alert(data.message || "Failed to update profile");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Failed to update profile. Please try again.");
        });
    });

    const cancelEditBtn  = document.getElementById('cancel-edit');

    cancelEditBtn.addEventListener('click', function () {
        editInfoFORM.style.display  = 'none';
        displayMode.style.display   = 'grid';
        actionButtons.style.display = 'flex';
    });


});

 function toggleVis(id, el) {
    const input = document.getElementById(id);
    const isHidden = input.type === 'password';
    input.type = isHidden ? 'text' : 'password';
    el.textContent = isHidden ? 'hide' : 'show';
  }

  function goToStep2() {
    const pw = document.getElementById('current-password');
    const err = document.getElementById('err-current');
    if (!pw.value) {
      pw.classList.add('error');
      err.style.display = 'block';
      pw.focus();
      return;
    }
    pw.classList.remove('error');
    err.style.display = 'none';
    document.getElementById('current-password-hidden').value = pw.value;

    document.getElementById('step-1').classList.remove('active');
    document.getElementById('step-2').classList.add('active');
    document.getElementById('dot-1').classList.remove('active');
    document.getElementById('dot-1').classList.add('done');
    document.getElementById('dot-2').classList.add('active');
    document.getElementById('card-title').textContent = 'New Password';
    document.getElementById('card-sub').textContent = 'Choose a strong, unique password';
  }

  function goBack() {
    document.getElementById('step-2').classList.remove('active');
    document.getElementById('step-1').classList.add('active');
    document.getElementById('dot-2').classList.remove('active');
    document.getElementById('dot-1').classList.remove('done');
    document.getElementById('dot-1').classList.add('active');
    document.getElementById('card-title').textContent = 'Verify Identity';
    document.getElementById('card-sub').textContent = 'Enter your current password to continue';
  }

  function checkStrength(val) {
    const fill = document.getElementById('strength-fill');
    const label = document.getElementById('strength-label');
    let score = 0;
    if (val.length >= 8)  score++;
    if (val.length >= 12) score++;
    if (/[A-Z]/.test(val)) score++;
    if (/[0-9]/.test(val)) score++;
    if (/[^A-Za-z0-9]/.test(val)) score++;

    const levels = [
      { pct: '0%',   color: 'transparent', text: '' },
      { pct: '20%',  color: '#c0574a',     text: 'Weak' },
      { pct: '40%',  color: '#c0574a',     text: 'Fair' },
      { pct: '60%',  color: '#c9a96e',     text: 'Moderate' },
      { pct: '80%',  color: '#c9a96e',     text: 'Strong' },
      { pct: '100%', color: '#5a9e7a',     text: 'Excellent' },
    ];

    const lvl = val.length === 0 ? 0 : Math.max(1, score);
    fill.style.width = levels[lvl].pct;
    fill.style.background = levels[lvl].color;
    label.textContent = levels[lvl].text;
    label.style.color = levels[lvl].color;
  }

  function submitForm() {
    const newPw  = document.getElementById('new-password');
    const confPw = document.getElementById('confirm-password');
    const errConf = document.getElementById('err-confirm');
    let valid = true;

    if (!newPw.value || newPw.value.length < 8) {
      newPw.classList.add('error');
      valid = false;
    } else { newPw.classList.remove('error'); }

    if (newPw.value !== confPw.value || !confPw.value) {
      confPw.classList.add('error');
      errConf.style.display = 'block';
      valid = false;
    } else {
      confPw.classList.remove('error');
      errConf.style.display = 'none';
    }

    if (!valid) return;

    const btn = document.querySelector('#step-2 .btn-primary');
    btn.classList.add('loading');
    btn.textContent = 'Updating…';

    // Simulate submission — swap for real form.submit() in production
    setTimeout(() => {
      document.getElementById('step-2').classList.remove('active');
      document.getElementById('dot-2').classList.remove('active');
      document.getElementById('dot-2').classList.add('done');
      document.getElementById('card-title').textContent = 'All Done';
      document.getElementById('card-sub').textContent = '';
      document.getElementById('success-view').classList.add('active');
      // For real submission: document.getElementById('change-password-form').submit();
    }, 1400);
  }
// Open modal
document.getElementById('change-password-btn').addEventListener('click', function () {
    document.getElementById('password-modal').classList.add('active');
    document.body.style.overflow = 'hidden'; // prevent background scrolling
});

// Close modal
function closePasswordModal() {
    document.getElementById('password-modal').classList.remove('active');
    document.body.style.overflow = '';

    // Reset form back to step 1
    document.getElementById('step-1').classList.add('active');
    document.getElementById('step-2').classList.remove('active');
    document.getElementById('success-view').classList.remove('active');
    document.getElementById('dot-1').classList.add('active');
    document.getElementById('dot-1').classList.remove('done');
    document.getElementById('dot-2').classList.remove('active');
    document.getElementById('card-title').textContent = 'Verify Identity';
    document.getElementById('card-sub').textContent = 'Enter your current password to continue';
    document.getElementById('current-password').value = '';
    document.getElementById('new-password').value = '';
    document.getElementById('confirm-password').value = '';
}

// Close when clicking the backdrop
document.getElementById('password-modal').addEventListener('click', function (e) {
    if (e.target === this) closePasswordModal();
});

// Close on Escape key
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closePasswordModal();
});
