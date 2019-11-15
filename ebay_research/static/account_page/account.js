
const switchToggle = {'none': 'block', 'block': 'none'};

function toggleRecurVisibility(){
  // Toggle visibility of recurring choice buttons
  // TODO: add hint of what to do i.e. select the search you would like to run on repeat
  let items = document.getElementsByClassName('hideRecurring');
  let displayMode = window.getComputedStyle(items[0]).getPropertyValue('display');
  displayMode = switchToggle[displayMode];
  for (let i = 0; i < items.length; i ++){
    items[i].style.display = displayMode;
  }
}
