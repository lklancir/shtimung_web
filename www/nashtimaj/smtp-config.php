<?php
/* SMTP pristup za nashtimaj leadove.
   Mailbox mora postojati u cPanelu (Email Accounts).
   Datoteka je u .gitignore i NE ide u git: lozinku upiši ovdje
   lokalno pa deployaj (deploy skripta je nosi na server). */
return [
    'host' => 'mail.shtimung.hr',
    'user' => 'info@shtimung.hr',
    'pass' => '', // ← upiši lozinku mailboxa
];
