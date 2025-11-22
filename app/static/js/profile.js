function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
}

document.getElementById('profileForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const data = {
        name: document.getElementById('name').value,
        phone: document.getElementById('phone').value,
        age: document.getElementById('age').value,
        gender: document.getElementById('gender').value,
        occupation: document.getElementById('occupation').value,
        location: document.getElementById('location').value
    };

    const res = await fetch('/api/profile', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(data)
    });

    const result = await res.json();

    if (result.success) {
        alert('Profile updated successfully!');
        document.getElementById('profileName').textContent = data.name;
    } else {
        alert('Error updating profile');
    }
});

document.getElementById('passwordForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const data = {
        current_password: document.getElementById('currentPassword').value,
        new_password: document.getElementById('newPassword').value
    };

    const res = await fetch('/api/change-password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(data)
    });

    const result = await res.json();

    if (result.success) {
        alert('Password changed successfully!');
        document.getElementById('passwordForm').reset();
    } else {
        alert(result.message || 'Error changing password');
    }
});
