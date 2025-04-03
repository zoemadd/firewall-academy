document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".fill-in-the-blank-form");
    const inputs = document.querySelectorAll(".fill-in-input");
    const resultDisplay = document.createElement("p");
    resultDisplay.classList.add("intro-text");
    form.appendChild(resultDisplay);

    // Load saved score from localStorage
    const savedScore = localStorage.getItem("fillInBlankScore");
    if (savedScore !== null) {
        resultDisplay.textContent = savedScore;
    }

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        let score = 0;
        let total = inputs.length;

        inputs.forEach(input => {
            const userAnswer = input.value.trim().toLowerCase();
            const correctAnswer = input.dataset.answer.toLowerCase();

            if (userAnswer === correctAnswer) {
                score++;
                input.style.borderColor = "green";
            } else {
                input.style.borderColor = "red";
            }
        });

        const scoreText = `You scored ${score} out of ${total}!`;
        resultDisplay.textContent = scoreText;
        localStorage.setItem("fillInBlankScore", scoreText); // Save score in localStorage
    });
});

