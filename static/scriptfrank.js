// Initialize the map
 // Handle form submission
document.getElementById('locationDropdown').addEventListener('change', function() {
    const location = this.value;
    centerLocation(location);

});