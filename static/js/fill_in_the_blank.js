document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".fill-in-the-blank-form");
    const inputs = document.querySelectorAll(".fill-in-input");
    const resultDisplay = document.createElement("p");
    resultDisplay.classList.add("intro-text");
    form.appendChild(resultDisplay);

    form.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent page reload

        let score = 0;
        let total = inputs.length;

        inputs.forEach(input => {
            const userAnswer = input.value.trim().toLowerCase();
            const correctAnswer = input.dataset.answer.toLowerCase();

            if (userAnswer === correctAnswer) {
                score++;
                input.style.borderColor = "green"; // Indicate correct answers
            } else {
                input.style.borderColor = "red"; // Indicate incorrect answers
            }
        });

        resultDisplay.textContent = `You scored ${score} out of ${total}!`;
    });
});
