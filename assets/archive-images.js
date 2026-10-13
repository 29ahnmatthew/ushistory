document.addEventListener('DOMContentLoaded',()=>{
 document.querySelectorAll('img[data-archive-img]').forEach(img=>{
  const fallback=img.closest('figure')?.querySelector('.archive-card-preview');
  const show=()=>{img.hidden=true;if(fallback)fallback.hidden=false};
  img.addEventListener('error',show);
  img.addEventListener('load',()=>{ if(img.naturalWidth<=1)show();else if(fallback)fallback.hidden=true; });
  if(img.complete && img.naturalWidth===0)show();
 });
});
