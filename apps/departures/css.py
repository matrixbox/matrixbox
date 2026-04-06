_css = """*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,-apple-system,sans-serif;background:#111125;color:#e8e8f0;line-height:1.5;font-size:14px}
.container{max-width:480px;margin:0 auto;padding:.5rem .75rem}
.card{background:#1c1c36;border:1px solid #2e2e4e;border-radius:14px;padding:1rem;margin-bottom:.6rem;box-shadow:0 4px 12px rgba(0,0,0,.35)}
.sh{background:linear-gradient(135deg,#f0b429 0%,#d4950a 100%);color:#111;padding:.5rem .85rem;border-radius:10px;font-weight:700;font-size:.85rem;text-align:center;letter-spacing:.01em}
.form-row{display:flex;gap:.65rem;flex-wrap:wrap}
.col{flex:1;min-width:110px}
label,.control-label{display:block;font-size:.75rem;color:#9999b8;margin-bottom:.2rem;font-weight:500;text-transform:uppercase;letter-spacing:.03em}
input[type=text],select,.form-control{width:100%;padding:.5rem .7rem;background:#14142a;border:1px solid #3a3a5c;border-radius:10px;color:#e8e8f0;font-size:.85rem;outline:none;transition:border .2s,box-shadow .2s}
input[type=text]:focus,select:focus,.form-control:focus{border-color:#f0b429;box-shadow:0 0 0 2px rgba(240,180,41,.15)}
input:disabled,select:disabled{opacity:.35}
.btn,button[type=button]{padding:.45rem .9rem;border:1px solid #3a3a5c;border-radius:10px;cursor:pointer;font-size:.8rem;font-weight:600;background:#252545;color:#e8e8f0;transition:all .15s}
.btn:hover,button[type=button]:hover{background:#2e2e52;border-color:#f0b429;color:#f0b429}
.btn:active,button[type=button]:active{transform:scale(.97)}
button:disabled,.btn:disabled{opacity:.3;cursor:not-allowed;transform:none}
.btn-primary{background:#007bff !important;color:#fff !important;border-color:#0066dd !important}
.btn-outline-secondary{background:transparent;border:1px solid #4a4a6a;color:#bbb}
.btn-outline-secondary:hover{border-color:#f0b429;color:#f0b429;background:rgba(240,180,41,.06)}
.btn-sm{padding:.25rem .55rem;font-size:.75rem}
.sw{display:flex;align-items:center;gap:.6rem;padding:.4rem 0;cursor:pointer}
.sw input[type=checkbox]{width:2.6rem;height:1.35rem;-webkit-appearance:none;appearance:none;background:#333;border-radius:1rem;position:relative;cursor:pointer;transition:.2s;flex-shrink:0;border:none}
.sw input[type=checkbox]::before{content:'';position:absolute;width:1.05rem;height:1.05rem;background:#777;border-radius:50%;top:.15rem;left:.15rem;transition:.2s}
.sw input[type=checkbox]:checked{background:#f0b429}
.sw input[type=checkbox]:checked::before{background:#fff;left:1.4rem}
.sw span{font-size:.85rem;color:#d0d0e8}
.l{display:inline-flex;align-items:center;width:3em;height:1.5em;font-size:1em;background:rgba(0,0,0,.7);border-radius:.75em;box-shadow:.125em .125em 0 .125em rgba(0,0,0,.3) inset;color:#f0b429;padding:.15em;transition:background .1s .3s,box-shadow .1s .3s;-webkit-appearance:none;appearance:none}
.l::after,.l::before{content:'';display:block}
.l::before{background:#d7d7d7;border-radius:50%;width:1.2em;height:1.2em;transition:background .1s .3s,transform .3s;z-index:1}
.l::after{background:linear-gradient(transparent 50%,rgba(0,0,0,.15) 0) 0 50%/50% 100%,repeating-linear-gradient(90deg,#bbb 0,#bbb,#bbb 20%,#999 20%,#999 40%) 0 50%/50% 100%,radial-gradient(circle at 50% 50%,#888 25%,transparent 26%);background-repeat:no-repeat;border:.25em solid transparent;border-left:.4em solid #d8d8d8;border-right:0 solid transparent;transition:border-left-color .1s .3s,transform .3s;transform:translateX(-22.5%);transform-origin:25% 50%;width:1.2em;height:1em;box-sizing:border-box}
.l:checked{background:rgba(0,0,0,.45);box-shadow:.125em .125em 0 .125em rgba(0,0,0,.1) inset}
.l:checked::before{background:currentColor;transform:translateX(125%)}
.l:checked::after{border-left-color:currentColor;transform:translateX(-2.5%) rotateY(180deg)}
.l:focus{outline:0}
.dropdown{position:relative;display:inline-block}
.dropbtn{background:#1c1c36;border:1px solid #3a3a5c;color:#e8e8f0;padding:.35rem .7rem;border-radius:10px;cursor:pointer;font-size:.85rem;transition:border .2s}
.dropbtn:hover{border-color:#f0b429}
.dropdown-content{display:none;position:absolute;left:0;background:#1c1c36;border:1px solid #3a3a5c;border-radius:10px;z-index:10;box-shadow:0 12px 32px rgba(0,0,0,.6);padding:.5rem;min-width:160px}
.dropdown:hover .dropdown-content{display:block}
.dd-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:.35rem}
.dd-grid img{cursor:pointer;border-radius:4px;border:2px solid transparent;transition:border .15s;display:block}
.dd-grid img:hover,.dd-grid img.dd-sel{border-color:#f0b429}
.dd-ops{margin-top:.4rem;border-top:1px solid #2e2e4e;padding-top:.4rem}
.dd-ops a{display:block;padding:.35rem .55rem;color:#d0d0e8;text-decoration:none;font-size:.85rem;border-radius:8px;white-space:nowrap;transition:background .15s}
.dd-ops a:hover{background:#252545;color:#f0b429}
green_box{display:inline-block;padding:3px 12px;background:linear-gradient(135deg,#15a535,#0d8a25);color:#fff;border-radius:8px;font-weight:700;font-size:.7rem;box-shadow:0 0 10px rgba(42,219,77,.3)}
red_box{display:inline-block;padding:3px 12px;background:linear-gradient(135deg,#b82e14,#8a2009);color:#fff;border-radius:8px;font-weight:700;font-size:.7rem;box-shadow:0 0 10px rgba(235,80,38,.3)}
.btn-check{display:none}
.btn-check+label.btn{display:inline-block;padding:3px 14px;border-radius:8px;opacity:.25;transition:.2s}
.btn-check:checked+label.btn{opacity:1}
.btn-danger{background:#dc3545 !important;color:#fff !important;border-color:#dc3545 !important}
.btn-success{background:#28a745 !important;color:#fff !important;border-color:#28a745 !important}
.form-check{padding:.25rem 0 .25rem 1.5rem;position:relative}
.form-check-input{position:absolute;left:0;margin-top:.35rem}
.form-check-label{margin-bottom:0;font-size:.85rem}
table{width:100%;border-collapse:collapse}
td{padding:.5rem .6rem;border-bottom:1px solid #232345;background:transparent;color:#d0d0e8;font-size:.8rem;vertical-align:middle}
td:first-child{color:#8888aa;font-size:.75rem;white-space:nowrap}
details>summary{cursor:pointer;color:#f0b429;font-size:.85rem;list-style:none;padding:.3rem 0;font-weight:600}
details[open]>summary{margin-bottom:.5rem}
hr{border:none;border-top:1px solid #2e2e4e;margin:.6rem 0}
.grp{margin-bottom:.7rem}
.grp-title{font-size:.65rem;text-transform:uppercase;letter-spacing:.06em;color:#6a6a88;margin-bottom:.4rem;font-weight:700}
.tt-row{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center}
.tt-col{display:flex;flex-direction:column;gap:.1rem}
a{color:#f0b429;text-decoration:none}a:hover{text-decoration:underline}
small{font-size:.8rem}
input[type=submit]{padding:.45rem .9rem;border:1px solid #3a3a5c;border-radius:10px;cursor:pointer;font-size:.8rem;background:#252545;color:#e8e8f0}
.scr-btn{background:#1c1c36;color:#8888aa;border:1px solid #3a3a5c;padding:3px 10px;border-radius:8px;font-size:13px;font-weight:700;cursor:pointer;transition:all .15s;margin:0 3px}
.scr-btn:hover{border-color:#f0b429;color:#f0b429}
.scr-btn.act{background:#28a745;color:#fff;border-color:#28a745}
.save-btn{width:100%;padding:.65rem;background:linear-gradient(135deg,#f0b429,#d4950a);color:#111;border:none;border-radius:10px;font-size:1rem;font-weight:700;cursor:pointer;transition:all .15s;box-shadow:0 2px 8px rgba(240,180,41,.3)}
.save-btn:hover{box-shadow:0 4px 16px rgba(240,180,41,.45);transform:translateY(-1px)}
.save-btn:active{transform:translateY(0);box-shadow:0 1px 4px rgba(240,180,41,.2)}
.spin{display:inline-block;width:.8rem;height:.8rem;border:2px solid #333;border-top-color:#f0b429;border-radius:50%;animation:sp .6s linear infinite}
@keyframes sp{to{transform:rotate(360deg)}}"""
