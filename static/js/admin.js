// Function to remove an image from the additional images grid
function removeImage(imageContainer) {
    if (confirm('Are you sure you want to remove this image?')) {
        imageContainer.remove();
    }
}

// Preview images before upload
function previewImage(input, previewContainer) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.classList.add('w-full', 'rounded', 'shadow');
            previewContainer.innerHTML = '';
            previewContainer.appendChild(img);
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

// Preview multiple images before upload
function previewMultipleImages(input, previewGrid) {
    if (input.files) {
        previewGrid.innerHTML = '';
        
        for (let i = 0; i < input.files.length; i++) {
            const reader = new FileReader();
            const file = input.files[i];
            
            reader.onload = function(e) {
                const div = document.createElement('div');
                div.className = 'relative';
                
                const img = document.createElement('img');
                img.src = e.target.result;
                img.classList.add('w-full', 'rounded', 'shadow');
                
                const removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.className = 'absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600';
                removeBtn.innerHTML = `
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                `;
                removeBtn.onclick = () => div.remove();
                
                div.appendChild(img);
                div.appendChild(removeBtn);
                previewGrid.appendChild(div);
            };
            
            reader.readAsDataURL(file);
        }
    }
}