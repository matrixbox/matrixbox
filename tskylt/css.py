_css = """@charset "UTF-8";

::-webkit-datetime-edit-day-field,
::-webkit-datetime-edit-fields-wrapper,
::-webkit-datetime-edit-hour-field,
::-webkit-datetime-edit-minute,
::-webkit-datetime-edit-month-field,
::-webkit-datetime-edit-text,
::-webkit-datetime-edit-year-field {
padding: 0
}
::-webkit-inner-spin-button {
height: auto
}
::-webkit-search-decoration {
-webkit-appearance: none
}
::-webkit-color-swatch-wrapper {
padding: 0
}
::-webkit-file-upload-button {
font: inherit;
-webkit-appearance: button
}
::file-selector-button {
font: inherit;
-webkit-appearance: button
}

.form-control[type=file]:not(:disabled):not([readonly]) {
cursor: pointer
}

 

.btn-check {
position: absolute;
clip: rect(0, 0, 0, 0);
pointer-events: none
}
.btn-check:disabled+.btn {
pointer-events: none;
filter: none;
opacity: .65
}


@media (prefers-reduced-motion:reduce) {
.btn {
transition: none
}
}
.btn:hover {
color: var(--bs-btn-hover-color);
background-color: var(--bs-btn-hover-bg);
border-color: var(--bs-btn-hover-border-color)
}
.btn-check+.btn:hover {
color: var(--bs-btn-color);
background-color: var(--bs-btn-bg);
border-color: var(--bs-btn-border-color)
}
.btn:focus-visible {
color: var(--bs-btn-hover-color);
background-color: var(--bs-btn-hover-bg);
border-color: var(--bs-btn-hover-border-color);
outline: 0;
box-shadow: var(--bs-btn-focus-box-shadow)
}
.btn-check:focus-visible+.btn {
border-color: var(--bs-btn-hover-border-color);
outline: 0;
box-shadow: var(--bs-btn-focus-box-shadow)
}
.btn-check:checked+.btn {
color: var(--bs-btn-active-color);
background-color: var(--bs-btn-active-bg);
border-color: var(--bs-btn-active-border-color)
}
.btn-check:checked+.btn:focus-visible,
.btn.show:focus-visible,
.btn:first-child:active:focus-visible,
:not(.btn-check)+.btn:active:focus-visible {
box-shadow: var(--bs-btn-focus-box-shadow)
}
.btn-check:checked:focus-visible+.btn {
box-shadow: var(--bs-btn-focus-box-shadow)
}
.btn:disabled {
color: var(--bs-btn-disabled-color);
pointer-events: none;
background-color: var(--bs-btn-disabled-bg);
border-color: var(--bs-btn-disabled-border-color);
opacity: var(--bs-btn-disabled-opacity)
}
.btn-primary {
--bs-btn-color: #fff;
--bs-btn-bg: #0d6efd;
--bs-btn-border-color: #0d6efd;
--bs-btn-hover-color: #fff;
--bs-btn-hover-bg: #0b5ed7;
--bs-btn-hover-border-color: #0a58ca;
--bs-btn-focus-shadow-rgb: 49, 132, 253;
--bs-btn-active-color: #fff;
--bs-btn-active-bg: #93beff;
--bs-btn-active-border-color: #93beff;
--bs-btn-active-shadow: inset 0 3px 5px rgba(0, 0, 0, 0.125);
--bs-btn-disabled-color: #fff;
--bs-btn-disabled-bg: #93beff;
--bs-btn-disabled-border-color: #0d6efd
}
.btn-success {
--bs-btn-color: #fff;
--bs-btn-bg: #198754;
--bs-btn-border-color: #198754;
--bs-btn-hover-color: #fff;
--bs-btn-hover-bg: #157347;
--bs-btn-hover-border-color: #146c43;
--bs-btn-focus-shadow-rgb: 60, 153, 110;
--bs-btn-active-color: #fff;
--bs-btn-active-bg: #b8ffde;
--bs-btn-active-border-color: #b8ffde;
--bs-btn-active-shadow: inset 0 3px 5px rgba(0, 0, 0, 0.125);
--bs-btn-disabled-color: #fff;
--bs-btn-disabled-bg: #198754;
--bs-btn-disabled-border-color: #198754
}
.btn-danger {
--bs-btn-color: #fff;
--bs-btn-bg: #dc3545;
--bs-btn-border-color: #dc3545;
--bs-btn-hover-color: #fff;
--bs-btn-hover-bg: #bb2d3b;
--bs-btn-hover-border-color: #b02a37;
--bs-btn-focus-shadow-rgb: 225, 83, 97;
--bs-btn-active-color: #fff;
--bs-btn-active-bg: #ffc3c9;
--bs-btn-active-border-color: #ffc3c9;
--bs-btn-active-shadow: inset 0 3px 5px rgba(0, 0, 0, 0.125);
--bs-btn-disabled-color: #fff;
--bs-btn-disabled-bg: #dc3545;
--bs-btn-disabled-border-color: #dc3545
}
*,
::after,
::before {
box-sizing: border-box
}
body {
margin: 0;
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
font-size: 1rem;
font-weight: 400;
line-height: 1.5;
color: #212529;
text-align: left;
background-color: #fff
}
button {
border-radius: 0
}
button:focus {
outline: 1px dotted;
outline: 5px auto -webkit-focus-ring-color
}
.container {
width: 100%;
padding-right: 15px;
padding-left: 0;
margin-right: auto;
margin-left: 0
}
@media (min-width:576px) {
.container {
max-width: 540px
}
}
@media (min-width:768px) {
.container {
max-width: 720px
}
}
@media (min-width:992px) {
.container {
max-width: 960px
}
}
@media (min-width:1200px) {
.container {
max-width: 1140px
}
}
.col,
.col-md-6 {
position: relative;
width: 100%;
padding-right: 15px;
padding-left: 15px
}
.col {
-ms-flex-preferred-size: 0;
flex-basis: 0;
-ms-flex-positive: 1;
flex-grow: 1;
max-width: 100%
}
@media (min-width:768px) {
.col-md-6 {
-ms-flex: 0 0 50%;
flex: 0 0 50%;
max-width: 50%
}
}
.form-control {
display: block;
width: 100%;
height: calc(1.5em + .75rem + 2px);
padding: .375rem .75rem;
font-size: 1rem;
font-weight: 400;
line-height: 1.5;
color: #495057;
background-color: #fff;
background-clip: padding-box;
border: 1px solid #ced4da;
border-radius: .25rem;
transition: border-color .15s ease-in-out, box-shadow .15s ease-in-out
}
@media (prefers-reduced-motion:reduce) {
.form-control {
transition: none
}
}
.form-control::-ms-expand {
background-color: transparent;
border: 0
}
.form-control:focus {
color: #495057;
background-color: #fff;
border-color: #80bdff;
outline: 0;
box-shadow: 0 0 0 .2rem rgba(0, 123, 255, .25)
}
.form-control::-webkit-input-placeholder {
color: #6c757d;
opacity: 1
}
.form-control::-moz-placeholder {
color: #6c757d;
opacity: 1
}
.form-control:-ms-input-placeholder {
color: #6c757d;
opacity: 1
}
.form-control::-ms-input-placeholder {
color: #6c757d;
opacity: 1
}
.form-control:disabled {
background-color: #e9ecef;
opacity: 1
}
select.form-control:focus::-ms-value {
color: #495057;
background-color: #fff
}
.form-group {
margin-bottom: 1rem
}
.form-row {
display: -ms-flexbox;
display: flex;
-ms-flex-wrap: wrap;
flex-wrap: wrap;
margin-right: -5px;
margin-left: -5px
}
.form-row>.col {
padding-right: 5px;
padding-left: 5px
}
.btn {
display: inline-block;
font-weight: 400;
color: #212529;
text-align: center;
vertical-align: middle;
-webkit-user-select: none;
-moz-user-select: none;
-ms-user-select: none;
user-select: none;
background-color: transparent;
border: 1px solid transparent;
padding: .375rem .75rem;
font-size: 1rem;
line-height: 1.5;
border-radius: .25rem;
transition: color .15s ease-in-out, background-color .15s ease-in-out, border-color .15s ease-in-out, box-shadow .15s ease-in-out
}
@media (prefers-reduced-motion:reduce) {
.btn {
transition: none
}
}
.btn:hover {
color: #212529;
text-decoration: none
}
.btn:focus {
outline: 0;
box-shadow: 0 0 0 .2rem rgba(0, 123, 255, .25)
}
.btn:disabled {
opacity: .65
}
.btn-primary {
color: #fff;
background-color: #007bff;
border-color: #007bff
}
.btn-primary:hover {
color: #fff;
background-color: #0069d9;
border-color: #0062cc
}
.btn-primary:focus {
box-shadow: 0 0 0 .2rem rgba(38, 143, 255, .5)
}
.btn-primary:disabled {
color: #fff;
background-color: #007bff;
border-color: #007bff
}
.btn-primary:not(:disabled):not(.disabled).active,
.btn-primary:not(:disabled):not(.disabled):active {
color: #fff;
background-color: #0062cc;
border-color: #005cbf
}
.btn-primary:not(:disabled):not(.disabled).active:focus,
.btn-primary:not(:disabled):not(.disabled):active:focus {
box-shadow: 0 0 0 .2rem rgba(38, 143, 255, .5)
}
.btn-secondary:not(:disabled):not(.disabled).active,
.btn-secondary:not(:disabled):not(.disabled):active {
color: #fff;
background-color: #aeaeae;
border-color: #4e555b
}
.btn-secondary:not(:disabled):not(.disabled).active:focus,
.btn-secondary:not(:disabled):not(.disabled):active:focus {
box-shadow: 0 0 0 .2rem rgba(130, 138, 145, .5)
}
.btn-success {
color: #fff;
background-color: #28a745;
border-color: #28a745
}
.btn-success:hover {
color: #fff;
background-color: #218838;
border-color: #1e7e34
}
.btn-success:focus {
box-shadow: 0 0 0 .2rem rgba(72, 180, 97, .5)
}
.btn-success:disabled {
color: #fff;
background-color: #28a745;
border-color: #28a745
}
.btn-success:not(:disabled):not(.disabled).active,
.btn-success:not(:disabled):not(.disabled):active {
color: #fff;
background-color: #1e7e34;
border-color: #1c7430
}
.btn-success:not(:disabled):not(.disabled).active:focus,
.btn-success:not(:disabled):not(.disabled):active:focus {
box-shadow: 0 0 0 .2rem rgba(72, 180, 97, .5)
}
.btn-warning:not(:disabled):not(.disabled).active,
.btn-warning:not(:disabled):not(.disabled):active {
color: #212529;
background-color: #d39e00;
border-color: #c69500
}
.btn-warning:not(:disabled):not(.disabled).active:focus,
.btn-warning:not(:disabled):not(.disabled):active:focus {
box-shadow: 0 0 0 .2rem rgba(222, 170, 12, .5)
}
.btn-danger {
color: #fff;
background-color: #dc3545;
border-color: #dc3545
}
.btn-danger:hover {
color: #fff;
background-color: #c82333;
border-color: #bd2130
}
.btn-danger:focus {
box-shadow: 0 0 0 .2rem rgba(225, 83, 97, .5)
}
.btn-danger:disabled {
color: #fff;
background-color: #dc3545;
border-color: #dc3545
}
.btn-danger:not(:disabled):not(.disabled).active,
.btn-danger:not(:disabled):not(.disabled):active {
color: #fff;
background-color: #bd2130;
border-color: #b21f2d
}
.btn-danger:not(:disabled):not(.disabled).active:focus,
.btn-danger:not(:disabled):not(.disabled):active:focus {
box-shadow: 0 0 0 .2rem rgba(225, 83, 97, .5)
}
.btn-dark:not(:disabled):not(.disabled).active,
.btn-dark:not(:disabled):not(.disabled):active {
color: #fff;
background-color: #1d2124;
border-color: #171a1d
}
.btn-dark:not(:disabled):not(.disabled).active:focus,
.btn-dark:not(:disabled):not(.disabled):active:focus {
box-shadow: 0 0 0 .2rem rgba(82, 88, 93, .5)
}
.btn-outline-primary:not(:disabled):not(.disabled).active,
.btn-outline-primary:not(:disabled):not(.disabled):active {
color: #fff;
background-color: #007bff;
border-color: #007bff
}
.btn-outline-primary:not(:disabled):not(.disabled).active:focus,
.btn-outline-primary:not(:disabled):not(.disabled):active:focus {
box-shadow: 0 0 0 .2rem rgba(0, 123, 255, .5)
}
.btn-outline-secondary {
color: #6c757d;
border-color: #6c757d
}
.btn-outline-secondary:hover {
color: #fff;
background-color: #6c757d;
border-color: #6c757d
}
.btn-outline-secondary:focus {
box-shadow: 0 0 0 .2rem rgba(108, 117, 125, .5)
}
.btn-outline-secondary:disabled {
color: #6c757d;
background-color: transparent
}
.btn-outline-secondary:not(:disabled):not(.disabled).active,
.btn-outline-secondary:not(:disabled):not(.disabled):active {
color: #fff;
background-color: #6c757d;
border-color: #6c757d
}
.btn-outline-secondary:not(:disabled):not(.disabled).active:focus,
.btn-outline-secondary:not(:disabled):not(.disabled):active:focus {
box-shadow: 0 0 0 .2rem rgba(108, 117, 125, .5)
}
.btn-outline-success:not(:disabled):not(.disabled).active,
.btn-outline-success:not(:disabled):not(.disabled):active {
color: #fff;
background-color: #28a745;
border-color: #28a745
}
.btn-outline-success:not(:disabled):not(.disabled).active:focus,
.btn-outline-success:not(:disabled):not(.disabled):active:focus {
box-shadow: 0 0 0 .2rem rgba(40, 167, 69, .5)
}
.btn-outline-warning:not(:disabled):not(.disabled).active,
.btn-outline-warning:not(:disabled):not(.disabled):active {
color: #212529;
background-color: #ffc107;
border-color: #ffc107
}
.btn-outline-warning:not(:disabled):not(.disabled).active:focus,
.btn-outline-warning:not(:disabled):not(.disabled):active:focus {
box-shadow: 0 0 0 .2rem rgba(255, 193, 7, .5)
}
.btn-outline-danger:not(:disabled):not(.disabled).active,
.btn-outline-danger:not(:disabled):not(.disabled):active {
color: #fff;
background-color: #dc3545;
border-color: #dc3545
}
.btn-outline-danger:not(:disabled):not(.disabled).active:focus,
.btn-outline-danger:not(:disabled):not(.disabled):active:focus {
box-shadow: 0 0 0 .2rem rgba(220, 53, 69, .5)
}
.btn-outline-dark:not(:disabled):not(.disabled).active,
.btn-outline-dark:not(:disabled):not(.disabled):active {
color: #fff;
background-color: #343a40;
border-color: #343a40
}
.btn-outline-dark:not(:disabled):not(.disabled).active:focus,
.btn-outline-dark:not(:disabled):not(.disabled):active:focus {
box-shadow: 0 0 0 .2rem rgba(52, 58, 64, .5)
}
.btn-sm {
padding: .25rem .5rem;
font-size: .875rem;
line-height: 1.5;
border-radius: .2rem
}
.custom-control {
position: relative;
display: block;
min-height: 1.5rem;
padding-left: 1.5rem
}
.custom-control-input {
position: absolute;
z-index: -1;
opacity: 0
}
.custom-control-input:checked~.custom-control-label::before {
color: #fff;
border-color: #007bff;
background-color: #007bff
}
.custom-control-input:focus~.custom-control-label::before {
box-shadow: 0 0 0 .2rem rgba(0, 123, 255, .25)
}
.custom-control-input:focus:not(:checked)~.custom-control-label::before {
border-color: #80bdff
}
.custom-control-input:not(:disabled):active~.custom-control-label::before {
color: #fff;
background-color: #b3d7ff;
border-color: #b3d7ff
}
.custom-control-input:disabled~.custom-control-label {
color: #6c757d
}
.custom-control-input:disabled~.custom-control-label::before {
background-color: #e9ecef
}
.custom-control-label {
position: relative;
margin-bottom: 0;
vertical-align: top
}
.custom-control-label::before {
position: absolute;
top: .25rem;
left: -1.5rem;
display: block;
width: 1rem;
height: 1rem;
pointer-events: none;
content: "";
background-color: #fff;
border: #adb5bd solid 1px
}
.custom-control-label::after {
position: absolute;
top: .25rem;
left: -1.5rem;
display: block;
width: 1rem;
height: 1rem;
content: "";
background: no-repeat 50%/50% 50%
}
.custom-switch {
padding-left: 2.25rem
}
.custom-switch .custom-control-label::before {
left: -2.25rem;
width: 1.75rem;
pointer-events: all;
border-radius: .5rem
}
.custom-switch .custom-control-label::after {
top: calc(.25rem + 2px);
left: calc(-2.25rem + 2px);
width: calc(1rem - 4px);
height: calc(1rem - 4px);
background-color: #adb5bd;
border-radius: .5rem;
transition: background-color .15s ease-in-out, border-color .15s ease-in-out, box-shadow .15s ease-in-out, -webkit-transform .15s ease-in-out;
transition: transform .15s ease-in-out, background-color .15s ease-in-out, border-color .15s ease-in-out, box-shadow .15s ease-in-out;
transition: transform .15s ease-in-out, background-color .15s ease-in-out, border-color .15s ease-in-out, box-shadow .15s ease-in-out, -webkit-transform .15s ease-in-out
}
@media (prefers-reduced-motion:reduce) {
.custom-switch .custom-control-label::after {
transition: none
}
}
.custom-switch .custom-control-input:checked~.custom-control-label::after {
background-color: #fff;
-webkit-transform: translateX(.75rem);
transform: translateX(.75rem)
}
.custom-switch .custom-control-input:disabled:checked~.custom-control-label::before {
background-color: rgba(0, 123, 255, .5)
}
.custom-control-label::before {
transition: background-color .15s ease-in-out, border-color .15s ease-in-out, box-shadow .15s ease-in-out
}
@media (prefers-reduced-motion:reduce) {
.custom-control-label::before {
transition: none
}
}
.bg-warning {
background-color: #ffc107 !important
}
@media (min-width:768px) {
.d-md-flex {
display: -ms-flexbox !important;
display: flex !important
}
}
@media (min-width:768px) {
.justify-content-md-end {
-ms-flex-pack: end !important;
justify-content: flex-end !important
}
}
.mb-0 {
margin-bottom: 0 !important
}
.p-1 {
padding: .25rem !important
}
.font-weight-bold {
font-weight: 700 !important
}
.text-dark {
color: #343a40 !important
}
@media print {
*,
::after,
::before {
text-shadow: none !important;
box-shadow: none !important
}
a:not(.btn) {
text-decoration: underline
}
@page {
size: a3
}
body {
min-width: 992px !important
}
.container {
min-width: 992px !important
}
}
body {
background-color: #111
}
form {
padding: 10px 10px 30px !important;
background: #ebeff2
}
table,
td {
border: 1px solid #dbdbdb;
border-collapse: collapse
}
td {
background-color: #dbdbdb
}
#rcorners0 {
border-radius: 0 10px 10px 10px;
box-shadow: grey +3px +2px
}
#rcorners1 {
border-radius: 10px;
box-shadow: grey +3px +2px
}
.l {
display: block;
margin-bottom: 1.5em;
font-size: 1em
}
.l {
background-color: rgba(0, 0, 0, .7);
border-radius: .75em;
box-shadow: .125em .125em 0 .125em rgba(0, 0, 0, .3) inset;
color: #fdea7b;
display: inline-flex;
align-items: center;
margin: auto;
padding: .15em;
width: 3em;
height: 1.5em;
transition: background-color .1s .3s ease-out, box-shadow .1s .3s ease-out;
-webkit-appearance: none;
-moz-appearance: none;
appearance: none
}
.l:after,
.l:before {
content: "";
display: block
}
.l:before {
background-color: #d7d7d7;
border-radius: 50%;
width: 1.2em;
height: 1.2em;
transition: background-color .1s .3s ease-out, transform .3s ease-out;
z-index: 1
}
.l:after {
background: linear-gradient(transparent 50%, rgba(0, 0, 0, .15) 0) 0 50%/50% 100%, repeating-linear-gradient(90deg, #bbb 0, #bbb, #bbb 20%, #999 20%, #999 40%) 0 50%/50% 100%, radial-gradient(circle at 50% 50%, #888 25%, transparent 26%);
background-repeat: no-repeat;
border: .25em solid transparent;
border-left: .4em solid #d8d8d8;
border-right: 0 solid transparent;
transition: border-left-color .1s .3s ease-out, transform .3s ease-out;
transform: translateX(-22.5%);
transform-origin: 25% 50%;
width: 1.2em;
height: 1em;
box-sizing: border-box
}
.l:checked {
background-color: rgba(0, 0, 0, .45);
box-shadow: .125em .125em 0 .125em rgba(0, 0, 0, .1) inset
}
.l:checked:before {
background-color: currentColor;
transform: translateX(125%)
}
.l:checked:after {
border-left-color: currentColor;
transform: translateX(-2.5%) rotateY(180deg)
}
.l:focus {
outline: 0
}
details>summary {
list-style: none
}
.button {
position: relative;
transition: all .3s ease-in-out;
box-shadow: 0 5px 5px rgba(0, 0, 0, .2);
padding-block: .1rem;
padding-inline: .3rem;
background-color: rgb(0 107 179);
border-radius: 9999px;
display: flex;
align-items: center;
justify-content: center;
color: #ffff;
gap: 10px;
font-weight: 700;
border: 3px solid #ffffff4d;
outline: 0;
overflow: hidden;
font-size: 11px
}
.icon {
width: 14px;
height: 14px;
transition: all .3s ease-in-out
}
.button:hover {
transform: scale(1.05);
border-color: #fff9
}
.button:hover .icon {
transform: translate(4px)
}
.button:hover::before {
animation: shine 1.5s ease-out infinite
}
.button::before {
content: "";
position: absolute;
width: 100px;
height: 100%;
background-image: linear-gradient(120deg, rgba(255, 255, 255, 0) 30%, rgba(255, 255, 255, .8), rgba(255, 255, 255, 0) 70%);
top: 0;
left: -100px;
opacity: .6
}
@keyframes shine {
0% {
left: -100px
}
60% {
left: 100%
}
to {
left: 100%
}
}

red_box {
	justify-content: center;
	align-items: center;
	font-weight: 700;
	color: #03e9f4;
	text-decoration: none;
	transition: 0s;
	overflow: hidden;
	position: relative;
	padding: 3px 3px;
	margin: 0 0;
	margin-right: 0;
	background: #942a0d;
	color: #fff;
	box-shadow: 0 0 5px #eb5026, 0 0 25px #eb5026, 0 0 50px #eb5026, 0 0 200px #eb5026;
	-webkit-box-reflect: below 1px linear-gradient(transition, #0005)
}


green_box {
justify-content: center;
align-items: center;
font-weight: 700;
color: #03e9f4;
text-decoration: none;
transition: 0s;
overflow: hidden;
position: relative;
padding: 3px 3px;
margin: 0 0;
margin-right: 0;
background: #0e9929;
color: #fff;
box-shadow: 0 0 5px #2adb4d, 0 0 25px #2adb4d, 0 0 50px #2adb4d, 0 0 200px #2adb4d;
-webkit-box-reflect: below 1px linear-gradient(transition, #0005)
}
.dropbtn {
background-color: #454545;
color: white;
padding-top: 0px;
padding-bottom: 0px;
padding-left: 5px;
padding-right: 5px;
font-size: 13px;
border: none;
}
.dropdown {
position: relative;
display: inline-block;
}
.dropdown-content {
display: none;
position: absolute;
background-color: #f1f1f1;
min-width: 200px;
box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
z-index: 1;
}
.dropdown-content a {
color: black;
padding: 2px 16px;
text-decoration: none;
display: block;
z-index: 1;
}
.dropdown-content a:hover {background-color: #ddd;}
.dropdown:hover .dropdown-content {display: block;}
.dropdown:hover .dropbtn {background-color: #8c8989;}"""
  