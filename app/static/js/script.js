function addTrick() {
  const entry = document.querySelector('.trick-entry');
  const clone = entry.cloneNode(true);
  clone.querySelectorAll('input').forEach(input => {
    if (input.type === 'number') input.value = 0;
    else input.value = '';
  });
  entry.parentElement.appendChild(clone);
}
