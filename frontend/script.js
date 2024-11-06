document.getElementById('registrationForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const login = document.getElementById('login').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('http://127.0.0.1:8000/sign_up', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                login: login,
                password: password
            }),
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById('message').innerText = 'Регистрация прошла успешно!';
        } else {
            document.getElementById('message').innerText = 'Ошибка: ' + data.message;
        }
    } catch (error) {
        document.getElementById('message').innerText = 'Ошибка сети: ' + error.message;
    }
});