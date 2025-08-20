// Portfolio functionality
let portfolioData = [];
let currentImageIndex = 0;

// Load portfolio data
async function loadPortfolio() {
    try {
        const response = await fetch('/static/portfolio.json');
        const data = await response.json();
        portfolioData = data.images || [];
        renderPortfolio();
    } catch (error) {
        console.error('Error loading portfolio:', error);
    }
}

// Render portfolio grid
function renderPortfolio(filter = 'all') {
    const grid = document.getElementById('portfolioGrid');
    grid.innerHTML = '';

    const filteredImages = filter === 'all' 
        ? portfolioData 
        : portfolioData.filter(img => 
            img.categories && img.categories.some(cat => 
                cat.name.toLowerCase() === filter.toLowerCase()
            )
        );

    filteredImages.forEach((image, index) => {
        const item = document.createElement('div');
        item.className = 'portfolio-item';
        item.innerHTML = `
            <img src="/static/${image.filename}" alt="${image.title}" loading="lazy">
            <div class="portfolio-overlay">
                <h3>${image.title}</h3>
                <p>${image.description}</p>
                <p>${image.categories ? image.categories[0].name : ''}</p>
            </div>
        `;
        
        item.addEventListener('click', () => openModal(index, filteredImages));
        grid.appendChild(item);
    });
}

// Filter functionality
document.addEventListener('DOMContentLoaded', function() {
    loadPortfolio();

    // Filter buttons
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons
            filterBtns.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            btn.classList.add('active');
            // Filter portfolio
            const filter = btn.getAttribute('data-filter');
            renderPortfolio(filter);
        });
    });

    // Modal functionality
    const modal = document.getElementById('imageModal');
    const closeBtn = document.querySelector('.close');
    const prevBtn = document.querySelector('.prev');
    const nextBtn = document.querySelector('.next');

    closeBtn.addEventListener('click', closeModal);
    prevBtn.addEventListener('click', () => navigateModal(-1));
    nextBtn.addEventListener('click', () => navigateModal(1));

    // Close modal when clicking outside
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (modal.style.display === 'block') {
            if (e.key === 'Escape') closeModal();
            if (e.key === 'ArrowLeft') navigateModal(-1);
            if (e.key === 'ArrowRight') navigateModal(1);
        }
    });

    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Modal functions
function openModal(index, images = portfolioData) {
    currentImageIndex = index;
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalTitle = document.getElementById('modalTitle');
    const modalDescription = document.getElementById('modalDescription');
    const modalCamera = document.getElementById('modalCamera');

    const image = images[index];
    modalImage.src = `/static/${image.filename}`;
    modalTitle.textContent = image.title;
    modalDescription.textContent = image.description;
    modalCamera.textContent = `${image.camera_make} | ${image.lens} | f/${image.aperture} | ISO ${image.iso}`;

    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modal = document.getElementById('imageModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

function navigateModal(direction) {
    const newIndex = currentImageIndex + direction;
    if (newIndex >= 0 && newIndex < portfolioData.length) {
        openModal(newIndex);
    }
}

// Contact form handling
document.querySelector('.contact-form form').addEventListener('submit', function(e) {
    e.preventDefault();
    alert('Thank you for your message! I will get back to you soon.');
    this.reset();
});

