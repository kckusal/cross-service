
/** Toggle 'is-active' class in modal,
 * and also toggle 'is-clipped' in html.
 */
function toggleModal(modal) {
    modal.classList.toggle('is-active');
    document.documentElement.classList.toggle('is-clipped');
}