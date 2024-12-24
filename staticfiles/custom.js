const imageParent = document.getElementById('product-zoom-gallery');
const imgContainer = document.getElementById("image-container");
const sizeSelect = document.getElementById('size')

const fetchSize = async (id) => {
    const response = await fetch(`/get-variant-sizes/${id}/`);
    const sizes = await response.json();
    return sizes;
}

// Function to fetch images based on variant ID
const fetchImage = async (id) => {
    const response = await fetch(`/get-variant-images/${id}/`);
    const images = await response.json();
    return images;
};

// Function to add images to the DOM and reinitialize zoom and popup functionality
const addToDom = (images) => {
    // Clear existing images
    imageParent.innerHTML = '';
    const imageFirst = images[0];

    // Update the main image container with the first image in the new set
    imgContainer.innerHTML = `
                                                    <img id="product-zoom" src="/media/${imageFirst.image}" data-zoom-image="/media/${imageFirst.image}" alt="product image">
                                                    <a href="#" id="btn-product-gallery" class="btn-product-gallery">
                                                        <i class="icon-arrows"></i>
                                                    </a>
                                                `;

    // Append each new image as a thumbnail in the gallery
    images.forEach((e, index) => {
        const elementTemplate = `
                                                        <a class="product-gallery-item choose-image ${index === 0 ? "active" : ""}" href="#" 
                                                           data-image="/media/${e.image}"
                                                           data-zoom-image="/media/${e.image}">
                                                           <img src="/media/${e.image}" alt="product side">
                                                        </a>
                                                    `;
        const range = document.createRange();
        const fragment = range.createContextualFragment(elementTemplate);
        imageParent.appendChild(fragment);
    });

    // Reinitialize the zoom plugin and popup functionality
    reinitializeZoom();
    addClickEvents();
    initializePopup();
};

// Updated reinitializeZoom function to ensure zoom applies to the selected image
const reinitializeZoom = () => {
    const mainImage = $('#product-zoom');

    // Remove any existing zoom instance and the zoom container
    if (mainImage.data('elevateZoom')) {
        mainImage.data('elevateZoom').remove();
        $('.zoomContainer').remove();  // This clears the zoom container
    }

    // Reapply the zoom effect to the new image with updated attributes
    mainImage.removeAttr('data-zoom-image'); // Clear the current data-zoom-image
    mainImage.attr('data-zoom-image', mainImage.attr('src')); // Set the data-zoom-image to the current src

    // Apply the zoom plugin with the updated settings
    mainImage.elevateZoom({
        zoomType: "inner",
        cursor: "crosshair"
    });
};

// In the addClickEvents function, make sure to call reinitializeZoom after updating the image
const addClickEvents = () => {
    const galleryItems = document.querySelectorAll('.product-gallery-item.choose-image');
    galleryItems.forEach(item => {
        item.addEventListener('click', function (event) {
            event.preventDefault();

            // Remove active class from all gallery items and set it on the clicked item
            galleryItems.forEach(el => el.classList.remove('active'));
            item.classList.add('active');

            // Update the main image source and zoom image
            const newImage = item.getAttribute('data-image');
            const mainImage = document.getElementById('product-zoom');

            // Update the main image src and data-zoom-image
            mainImage.src = newImage;
            mainImage.setAttribute('data-zoom-image', newImage);

            // Reinitialize the zoom functionality after updating the image
            reinitializeZoom();
        });
    });
};


// Function to initialize popup gallery functionality
const initializePopup = () => {
    const galleryButton = document.getElementById('btn-product-gallery');
    galleryButton.addEventListener('click', function (event) {
        event.preventDefault();
        // Assuming magnificPopup or similar is used for the popup gallery
        $.magnificPopup.open({
            items: [
                // Collect all images for popup gallery
                ...Array.from(document.querySelectorAll('.product-gallery-item')).map((item) => ({
                    src: item.getAttribute('data-zoom-image'),
                    type: 'image'
                }))
            ],
            gallery: {
                enabled: true
            },
            type: 'image'
        });
    });
};

const updateSize = (sizes) => {
    sizeSelect.innerHTML = '<option value="">Select a size</option>';
    sizes.forEach((size) => {
        sizeSelect.innerHTML += `<option value="${size.size}">${size.size}</option>`;
    });
}
// Button click handler to load images based on color variant selection
const buttonClicked = async (id) => {
    const images = await fetchImage(id);
    const sizes = await fetchSize(id)
    updateSize(sizes)
    console.log(sizes)
    addToDom(images);
};



