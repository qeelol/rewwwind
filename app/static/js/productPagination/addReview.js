// add review, probably reuse for update
const ratingScore = document.getElementById('rating');

const stars = Array.from(document.querySelectorAll('.review__modal .bi-star-fill'));

function fillStars() {
    stars.forEach((star, index) => {
        star.style.color = '#D9D9D9';
        star.addEventListener('click', () => {
            if (star.style.color === 'orange') {
                const grayStar = stars.find(star => star.style.color === '#D9D9D9');
                stars.slice(index+1, grayStar).forEach(star => star.style.color = '#D9D9D9');
            } else {
                stars.slice(0, index+1).forEach(star => star.style.color = 'orange');
            }
            ratingScore.value = index + 1;
            console.log(ratingScore, ratingScore.value)
        })
    });
}


var modalOpen = false
function toggleModal() {
    modalOpen = !modalOpen
    const overlay = document.querySelector('.overlay');
    const modal = document.querySelector('.review__modal');

    if (window.location.href.includes('add-review') || window.location.href.includes('update-review') || window.location.href.includes('delete-review')) {
        window.location.href = `../${document.getElementById('get-id-here').getAttribute('product-id')}`
    }

    if (modal.style.display === 'block') {
        overlay.style.display = 'none';
        modal.style.display = 'none';

        stars.forEach(star => star.style.color = '#D9D9D9');
        document.getElementById('rating').value = null;
        document.getElementById('show_username').checked = false;
        document.getElementById('description').value = '';
    } else {
        overlay.style.display = 'block';
        modal.style.display = 'block';
    }
}

// open modal
const reviewButton = document.querySelector('.review__section .header__right .write');
reviewButton.addEventListener('click', () => toggleModal());

// close modal
const closeButton1 = document.getElementById('cancel');
const closeButton2 = document.querySelector('.review__modal i.bi-x-lg');
closeButton1.addEventListener('click', () => toggleModal());
closeButton2.addEventListener('click', () => toggleModal());

if (!window.location.href.includes('delete-review')) {
    if (window.location.href.includes('update-review')) {
        stars.slice(0, parseInt(document.getElementById('rating').value)).forEach(star => star.style.color = 'orange');
        document.getElementById('add-review').action = window.location.href;
    }
    fillStars();
}
