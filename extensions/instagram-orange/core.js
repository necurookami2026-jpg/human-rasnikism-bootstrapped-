/* Original implementation; no third-party extension code. */
(function(root){
 const instagram = value => {try {const u=new URL(value);return u.protocol==='https:' && ['instagram.com','www.instagram.com'].includes(u.hostname);}catch{return false;}};
 const mediaURL = value => {try {const u=new URL(value);return u.protocol==='https:' && !u.username && !u.password && ['cdninstagram.com','fbcdn.net'].some(h=>u.hostname===h||u.hostname.endsWith('.'+h)) ? u.href : null;}catch{return null;}};
 const unique = items => [...new Map(items.filter(x=>mediaURL(x.url)).map(x=>[x.url,{url:mediaURL(x.url),kind:x.kind==='video'?'video':'image'}])).values()].slice(0,200);
 const filename=(item,index)=>'RasnikiInstagram/media-'+String(index+1).padStart(3,'0')+(item.kind==='video'?'.mp4':'.jpg');
 const api={instagram,mediaURL,unique,filename}; root.OrangeCore=api;if(typeof module!=='undefined')module.exports=api;
})(globalThis);
