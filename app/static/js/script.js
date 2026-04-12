document.addEventListener("DOMContentLoaded", function () {
    const counters = document.querySelectorAll(".counter");

    counters.forEach(counter => {
        const updateCount = () => {
            const target = +counter.getAttribute("data-target");
            const count = +counter.innerText;

            const increment = Math.ceil(target / 100);

            if (count < target) {
                counter.innerText = Math.min(count + increment, target);
                setTimeout(updateCount, 20);
            } else {
                counter.innerText = target;
            }
        };

        updateCount();
    });
});

// ================= GALLERY SCROLL ANIMATION =================

document.addEventListener("DOMContentLoaded", function () {

    const items = document.querySelectorAll(".gallery-item");

    function revealOnScroll() {
        const triggerBottom = window.innerHeight * 0.85;

        items.forEach(item => {
            const boxTop = item.getBoundingClientRect().top;

            if (boxTop < triggerBottom) {
                item.classList.add("show");
            }
        });
    }

    window.addEventListener("scroll", revealOnScroll);
    revealOnScroll(); // trigger on load
});


function openModal(src) {
    document.getElementById("imageModal").style.display = "block";
    document.getElementById("modalImage").src = src;
}

function closeModal() {
    document.getElementById("imageModal").style.display = "none";
}