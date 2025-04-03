document.addEventListener("DOMContentLoaded", function () {
    const draggables = document.querySelectorAll(".drag-item");
    const dropZones = document.querySelectorAll(".drop-zone");
    const submitButton = document.getElementById("submit-drag-drop");
    const resultDisplay = document.getElementById("drag-drop-result");

    draggables.forEach(draggable => {
        draggable.addEventListener("dragstart", function (event) {
            event.dataTransfer.setData("text/plain", event.target.dataset.category);
            event.dataTransfer.setData("id", event.target.id);
            setTimeout(() => event.target.classList.add("hidden"), 0); // Hides the item temporarily while dragging
        });

        draggable.addEventListener("dragend", function (event) {
            event.target.classList.remove("hidden");
        });
    });

    dropZones.forEach(zone => {
        zone.addEventListener("dragover", function (event) {
            event.preventDefault(); // Allows drop
        });

        zone.addEventListener("drop", function (event) {
            event.preventDefault();
            const draggedCategory = event.dataTransfer.getData("text/plain");
            const draggedItemId = event.dataTransfer.getData("id");
            const draggedElement = document.getElementById(draggedItemId);

            if (draggedElement) {
                this.appendChild(draggedElement);
            }
        });
    });

    submitButton.addEventListener("click", function () {
        let score = 0;
        let totalItems = 0;

        dropZones.forEach(zone => {
            const correctCategory = zone.dataset.correctCategory;
            const droppedItems = zone.querySelectorAll(".drag-item");

            droppedItems.forEach(item => {
                totalItems++;
                if (item.dataset.category === correctCategory) {
                    score++;
                    item.style.border = "3px solid green"; // Green outline for correct
                } else {
                    item.style.border = "3px solid red"; // Red outline for incorrect
                }
            });
        });

        resultDisplay.textContent = `You scored ${score} out of ${totalItems}!`;
    });
});

