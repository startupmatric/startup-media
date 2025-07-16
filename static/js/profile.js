document.addEventListener('DOMContentLoaded', () => {
  const triggers = document.querySelectorAll('.tab-trigger');
  const contents = document.querySelectorAll('.tab-content');

  triggers.forEach(trigger => {
    trigger.addEventListener('click', () => {
      const tab = trigger.getAttribute('data-tab');

      contents.forEach(content => {
        content.classList.toggle('active', content.id === tab);
      });
    });
  });
});
