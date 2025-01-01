class DeleteProduct {
    constructor(product) {
        this.product = product;
        this.productID = product.getAttribute('product-id');
        this.openModalBtn = product.querySelector('i.bi-trash-fill');

        // target product-related stuff
        this.formContainer = document.querySelector('div.delete__form-container');
        this.form = this.formContainer.querySelector('form.delete__form');
        this.input = this.form.querySelector('input#deleteConfirm');
        this.inputID = this.form.querySelector('input#productID');
        this.formData = null;
        this.productDisplay = this.formContainer.querySelector('.product');
        this.closeModalBtn1 = this.formContainer.querySelector('.bi-x-lg');
        this.closeModalBtn2 = this.formContainer.querySelector('.cancel_button input');
        this.overlay = document.querySelector('.overlay');
        this.active = false;

        // bind to avoid annonymity issues
        this.handleKeyboard = this.handleKeyboard.bind(this);
        this.toggleForm = this.toggleForm.bind(this);

        this.redirect = false;

        this.init();
    }

    // initialise event listeners
    init() {
        this.openModalBtn.addEventListener('click', () => this.toggleForm());

        this.form.addEventListener('submit', (event) => this.handleSubmit(event));
        if (this.formContainer.style.display === 'flex' && this.formContainer.id === this.productID || this.formContainer.classList.contains('success')) {
            this.toggleForm();
            this.redirect = true;
        };
    }

    toggleForm() {
        if (!this.active) {
            this.formContainer.style.display = 'flex';
            this.overlay.style.display = 'block';

            document.addEventListener('keydown', this.handleKeyboard);
            this.closeModalBtn1.addEventListener('click', this.toggleForm);
            this.closeModalBtn2.addEventListener('click', this.toggleForm);

            // display target product
            const thumbnail = this.product.querySelector('.thumbnail').cloneNode(true);
            const identifier = this.product.querySelector('.name').cloneNode(true);
            this.productDisplay.appendChild(thumbnail);
            this.productDisplay.appendChild(identifier);

            this.form.id = this.productID;
        } else {
            this.formContainer.style.display = 'none';
            this.overlay.style.display = 'none';
            
            document.removeEventListener('keydown', this.handleKeyboard);
            this.closeModalBtn1.removeEventListener('click', this.toggleForm);
            this.closeModalBtn2.removeEventListener('click', this.toggleForm);

            // reset display and form
            this.productDisplay.innerHTML = '';
            this.input.value = '';

            if (this.redirect) {window.location.href = '../manage-products'};
        };

        this.active = !this.active;
    }

    // close if escape
    handleKeyboard(e) {
        if (e.key === 'Escape') {
            e.preventDefault();
            this.toggleForm();
        };
    }

    // custom form submission
    async handleSubmit(event) {
        if (this.productID == this.form.id) {        
            this.formData = new FormData();
            const formElements = this.form.querySelectorAll('input, select, textarea');
            this.inputID.value = this.productID;
            formElements.forEach(element => {
                this.formData.append(element.name, element.value);
            });
    
            // Debugging: Log the form data
            // for (let [key, value] of formData.entries()) {
            //     console.log(`${key}:`, value);
            // }
    
            const response = await fetch('/dashboard/manage-products/delete-product', {
                method: 'POST',
                body: this.formData,
            });
    
            await response.text();
            // const result = await response.text();
            // console.log(result);
        }
    }
};

const rows = Array.from(document.querySelectorAll('.products tbody tr'));
rows.forEach(row => new DeleteProduct(row));