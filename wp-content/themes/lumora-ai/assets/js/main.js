// Minimal intersection animation trigger
document.querySelectorAll('[data-io]')?.forEach((el)=>{
  const io = new IntersectionObserver(([entry])=>{
    if(entry.isIntersecting){
      el.classList.add('in');
      io.disconnect();
    }
  },{threshold: .2});
  io.observe(el);
});

// Defer non-critical third-party scripts example hook (user to implement)
window.lumoraLoadMarketing = function(){
  // e.g., load GA/Meta after consent
};

