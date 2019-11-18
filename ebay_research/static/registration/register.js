// States should only be visible if the location value = USA
const watch_select = document.getElementById('location');

watch_select.addEventListener('change', function () {
  let value = watch_select.options[watch_select.selectedIndex].value;
  if (value === 'USA') {
    document.getElementById('state').style.display = 'block';
  } else {
    document.getElementById('state').style.display = 'none';
  }
});