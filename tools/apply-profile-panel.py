# One-off patch: replace the cramped Leaflet popup with a venue profile panel
# that mirrors the native app's detail sheet (desktop side panel, mobile bottom sheet).
# Run once per copy:  python tools/apply-profile-panel.py path/to/index.html
import io, sys

path = sys.argv[1]
s = io.open(path, encoding='utf-8').read()

def replace_once(old, new, label):
    global s
    assert s.count(old) == 1, f"{label}: expected exactly one match, found {s.count(old)}"
    s = s.replace(old, new)

# ---------------------------------------------------------------- CSS
CSS = r"""
        /* ===== Venue profile (mirrors the native app's detail sheet) ===== */
        #container { position: relative; }
        #profile-panel {
            position: absolute; top: 0; left: 0; bottom: 0; width: 350px;
            background: #fff; z-index: 1003; display: flex; flex-direction: column;
            transform: translateX(-100%); visibility: hidden;
            transition: transform .28s cubic-bezier(.2,.8,.2,1), visibility 0s linear .28s;
            box-shadow: 2px 0 12px rgba(0,0,0,.12);
        }
        #profile-panel.open { transform: translateX(0); visibility: visible; transition: transform .28s cubic-bezier(.2,.8,.2,1); }
        #profile-scroll { flex: 1; min-height: 0; overflow-y: auto; overflow-x: hidden; -webkit-overflow-scrolling: touch; scrollbar-width: thin; }
        .profile-hero { position: relative; height: 230px; background: #eef2fb; flex-shrink: 0; overflow: hidden; }
        .profile-hero .venue-slider { position: absolute; inset: 0; margin: 0; border-radius: 0; height: 100%; }
        .profile-hero .slider-container { height: 100%; scrollbar-width: none; }
        .profile-hero .slider-container::-webkit-scrollbar { display: none; }
        .profile-hero .venue-slider img { height: 100%; width: 100%; }
        .profile-hero .slider-arrow { opacity: 0; transition: opacity .2s; }
        .profile-hero:hover .slider-arrow { opacity: 1; }
        .profile-hero .slider-dots { bottom: 6px; z-index: 3; }
        .profile-hero-overlay {
            position: absolute; left: 0; right: 0; bottom: 0; padding: 64px 18px 30px;
            background: linear-gradient(to top, rgba(0,0,0,.72) 0%, rgba(0,0,0,.35) 55%, transparent 100%);
            z-index: 2; pointer-events: none;
        }
        .profile-name { margin: 0 0 3px; font-size: 22px; font-weight: 700; color: #fff; line-height: 1.2; text-shadow: 0 1px 4px rgba(0,0,0,.35); }
        .profile-address { margin: 0; font-size: 13px; color: rgba(255,255,255,.92); text-shadow: 0 1px 2px rgba(0,0,0,.3); }
        .profile-hero-empty { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; color: #1E52BA; opacity: .35; }
        .profile-hero-empty svg { width: 56px; height: 56px; stroke: currentColor; fill: none; stroke-width: 1.5; }
        .profile-close {
            position: absolute; top: 12px; right: 12px; width: 36px; height: 36px; border-radius: 50%;
            background: rgba(0,0,0,.5); border: none; cursor: pointer; z-index: 6;
            display: flex; align-items: center; justify-content: center;
            backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px); transition: background .2s;
        }
        .profile-close:hover { background: rgba(0,0,0,.72); }
        .profile-close:focus-visible { outline: 2px solid #fff; outline-offset: 2px; }
        .profile-close svg { width: 18px; height: 18px; stroke: #fff; stroke-width: 2.5; fill: none; stroke-linecap: round; }
        .profile-grabber { display: none; }
        .profile-content { padding: 4px 18px 26px; }
        .profile-actions { display: flex; justify-content: center; gap: 18px; padding: 14px 0 4px; }
        .profile-action { display: flex; flex-direction: column; align-items: center; gap: 6px; text-decoration: none; color: inherit; -webkit-tap-highlight-color: transparent; }
        .profile-action .icon-circle { width: 48px; height: 48px; border-radius: 50%; background: #eef2fb; display: flex; align-items: center; justify-content: center; transition: background .2s, transform .15s; }
        .profile-action:hover .icon-circle { background: #dfe7f8; transform: translateY(-1px); }
        .profile-action:focus-visible .icon-circle { outline: 2px solid #1E52BA; outline-offset: 2px; }
        .profile-action .icon-circle svg { width: 20px; height: 20px; stroke: #1E52BA; fill: none; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
        .profile-action .icon-label { font-size: 12px; color: #555; font-weight: 500; }
        .profile-section { margin-top: 18px; }
        .profile-section-title { margin: 0 0 10px; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: .6px; color: #888; }
        .profile-description { margin: 0; font-size: 14.5px; line-height: 1.6; color: #333; }
        .profile-info-row { display: flex; gap: 10px; padding: 10px 0; border-bottom: 1px solid #eee; font-size: 13.5px; line-height: 1.45; }
        .profile-info-row:last-child { border-bottom: none; }
        .profile-info-label { flex: 0 0 90px; font-weight: 600; color: #666; }
        .profile-info-value { color: #333; min-width: 0; }
        .profile-info-value.seasonal { color: #BA1E1E; font-weight: 600; }
        .profile-tags { display: flex; flex-wrap: wrap; gap: 8px; }
        .profile-tag { display: inline-flex; align-items: center; padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: 500; color: #1E52BA; background: #eef2fb; }
        .leaflet-marker-icon.marker-active { filter: drop-shadow(0 6px 8px rgba(30,82,186,.5)); z-index: 1000 !important; }
        .fs-tooltip { background: #1E52BA; color: #fff; border: none; border-radius: 8px; padding: 6px 10px; font-weight: 600; font-size: 13px; box-shadow: 0 4px 12px rgba(0,0,0,.18); }
        .fs-tooltip::before { border-top-color: #1E52BA; }
        @media (max-width: 768px) {
            #profile-panel {
                position: fixed; top: auto; left: 0; right: 0; bottom: 0; width: 100%;
                height: 64dvh; max-height: 94dvh; border-radius: 18px 18px 0 0;
                transform: translateY(105%); box-shadow: 0 -6px 24px rgba(0,0,0,.22);
                transition: transform .3s cubic-bezier(.2,.8,.2,1), height .25s ease, visibility 0s linear .3s;
            }
            #profile-panel.open { transform: translateY(0); transition: transform .3s cubic-bezier(.2,.8,.2,1), height .25s ease; }
            #profile-panel.full { height: 94dvh; }
            .profile-grabber { display: flex; position: absolute; top: 0; left: 0; right: 0; height: 26px; justify-content: center; align-items: flex-start; padding-top: 7px; z-index: 6; touch-action: none; }
            .profile-grabber span { width: 42px; height: 5px; border-radius: 3px; background: rgba(255,255,255,.9); box-shadow: 0 1px 3px rgba(0,0,0,.35); }
            .profile-hero { height: 210px; border-radius: 18px 18px 0 0; }
            .profile-hero .slider-arrow { display: none !important; }
            .profile-close { top: 14px; right: 14px; }
            .profile-content { padding-bottom: calc(28px + env(safe-area-inset-bottom, 0px)); }
        }
        @media (prefers-reduced-motion: reduce) {
            #profile-panel, .profile-action .icon-circle, .profile-hero .slider-arrow { transition: none; }
        }
    </style>"""
replace_once("    </style>", CSS, "css")

# ---------------------------------------------------------------- HTML
PANEL = r"""        <aside id="profile-panel" role="dialog" aria-modal="false" aria-hidden="true" aria-label="Venue profile">
            <div class="profile-grabber" id="profile-grabber" aria-hidden="true"><span></span></div>
            <button class="profile-close" id="profile-close" type="button" aria-label="Close">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </button>
            <div id="profile-scroll"></div>
        </aside>

        <div style="position: relative; flex: 1;">"""
replace_once('        <div style="position: relative; flex: 1;">', PANEL, "panel markup")

# ---------------------------------------------------------------- JS: marker binding
OLD_BIND = """                    marker.bindPopup(createPopup(venue), {
                        className: 'custom-popup',
                        maxWidth: 340,
                        minWidth: 240,
                        autoPanPaddingTopLeft: [40, 40],
                        autoPanPaddingBottomRight: [40, 40]
                    });
                    marker.on('popupopen', (e) => {
                        trackEvent('profile_open', getVenueAnalyticsParams(venue));
                        const target = e.popup.getLatLng();
                        map.panTo(target, { animate: true });
                        // Nudge popup fully into view; try a stronger upward pan
                        setTimeout(() => map.panBy([0, -140], { animate: true }), 150);

                        const sliderEl = e.popup.getElement()?.querySelector('.slider-container');
                        attachSliderScrollSync(sliderEl);
                    });
"""
NEW_BIND = """                    marker.on('click', () => openProfile(venue, 'marker'));
                    if (!isMobile()) {
                        marker.bindTooltip(venue.name, { direction: 'top', offset: [0, -40], className: 'fs-tooltip', opacity: 1 });
                    }
"""
replace_once(OLD_BIND, NEW_BIND, "marker binding")

# keep the active marker highlighted after filters re-render the cluster layer,
# and close the profile if its venue was filtered out
OLD_COUNT = """            // Update count
            lastVisibleVenueCount = visibleCount;"""
NEW_COUNT = """            refreshActiveMarker();
            if (activeVenue && !venueMatchesFilters(activeVenue)) closeProfile();

            // Update count
            lastVisibleVenueCount = visibleCount;"""
replace_once(OLD_COUNT, NEW_COUNT, "update count hook")

# ---------------------------------------------------------------- JS: search selection
replace_once("""                    if (marker) {
                        marker.marker.openPopup();
                    }""", """                    if (marker) {
                        openProfile(marker.venue, 'search');
                    }""", "search select")

# ---------------------------------------------------------------- JS: profile implementation
PROFILE_JS = r"""
        // ===== Venue profile panel (desktop side panel / mobile bottom sheet) =====
        const profileStrings = {
            de: { navigate: 'Route', call: 'Anrufen', website: 'Webseite', instagram: 'Instagram', features: 'Ausstattung', note: 'Hinweis' },
            fr: { navigate: 'Itinéraire', call: 'Appeler', website: 'Site web', instagram: 'Instagram', features: 'Équipement', note: 'Remarque' },
            en: { navigate: 'Navigate', call: 'Call', website: 'Website', instagram: 'Instagram', features: 'Features', note: 'Note' }
        };
        const ps = (key) => (profileStrings[currentLang] || profileStrings.en)[key] || profileStrings.en[key];
        const profilePanel = document.getElementById('profile-panel');
        const profileScroll = document.getElementById('profile-scroll');
        const profileClose = document.getElementById('profile-close');
        const profileGrabber = document.getElementById('profile-grabber');
        let activeVenue = null;

        const profileIcons = {
            navigate: '<svg viewBox="0 0 24 24"><path d="M3 11l19-9-9 19-2-8-8-2z"/></svg>',
            call: '<svg viewBox="0 0 24 24"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/></svg>',
            website: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>',
            instagram: '<svg viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1112.63 8 4 4 0 0116 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/></svg>',
            photo: '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="10" r="2"/><path d="M21 15l-5-5-8 8"/></svg>'
        };

        function escapeHtmlText(value) {
            return String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
        }

        function formatHoursLines(hours) {
            return String(hours || '').split(/\s*(?:;|\||\n)\s*/).filter(Boolean).map(escapeHtmlText).join('<br>');
        }

        function createProfileContent(venue) {
            const partnerId = escapeHtmlAttribute(getPartnerId(venue));
            const mapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(venue.address)}`;
            const phoneHref = formatPhoneHref(venue.phone);
            const seasonalNote = venue.seasonalNote
                ? (venue.seasonalNote[currentLang] || venue.seasonalNote.en || venue.seasonalNote.de)
                : null;

            let heroInner = '';
            if (venue.images && venue.images.length > 0) {
                const sliderId = 'profile-slider';
                const imagesHtml = venue.images.map((img, i) =>
                    `<img src="${escapeHtmlAttribute(resolveVenueAssetUrl(img))}" alt="" loading="${i === 0 ? 'eager' : 'lazy'}" decoding="async" ${i === 0 ? 'fetchpriority="high"' : ''}>`
                ).join('');
                const dotsHtml = venue.images.map((_, i) => `<span class="slider-dot ${i === 0 ? 'active' : ''}" data-slide="${i}"></span>`).join('');
                heroInner = `
                    <div class="venue-slider" id="${sliderId}">
                        <div class="slider-container">${imagesHtml}</div>
                        ${venue.images.length > 1 ? `
                            <button class="slider-arrow prev" type="button" aria-label="Previous photo" onclick="slideImage('${sliderId}', -1)">‹</button>
                            <button class="slider-arrow next" type="button" aria-label="Next photo" onclick="slideImage('${sliderId}', 1)">›</button>
                            <div class="slider-dots">${dotsHtml}</div>` : ''}
                    </div>`;
            } else {
                heroInner = `<div class="profile-hero-empty">${profileIcons.photo}</div>`;
            }

            const actions = [
                `<a class="profile-action" href="${mapsUrl}" target="_blank" rel="noopener noreferrer" data-analytics-action="directions_click" data-partner-id="${partnerId}"><span class="icon-circle">${profileIcons.navigate}</span><span class="icon-label">${ps('navigate')}</span></a>`
            ];
            if (phoneHref) actions.push(`<a class="profile-action" href="${escapeHtmlAttribute(phoneHref)}" data-analytics-action="call_click" data-partner-id="${partnerId}"><span class="icon-circle">${profileIcons.call}</span><span class="icon-label">${ps('call')}</span></a>`);
            if (venue.website) actions.push(`<a class="profile-action" href="${escapeHtmlAttribute(venue.website)}" target="_blank" rel="noopener noreferrer" data-analytics-action="website_click" data-partner-id="${partnerId}"><span class="icon-circle">${profileIcons.website}</span><span class="icon-label">${ps('website')}</span></a>`);
            if (venue.instagram) actions.push(`<a class="profile-action" href="${escapeHtmlAttribute(venue.instagram)}" target="_blank" rel="noopener noreferrer" data-analytics-action="instagram_click" data-partner-id="${partnerId}"><span class="icon-circle">${profileIcons.instagram}</span><span class="icon-label">${ps('instagram')}</span></a>`);

            const tags = Object.entries(venue.filters || {}).flatMap(([category, values]) =>
                values.map(v => {
                    const def = filterDefinitions[category]?.find(f => f.id === v);
                    const translated = translate(`filters.options.${category}.${v}`, def?.label || v);
                    const label = typeof translated === 'function' ? translated() : translated;
                    return `<span class="profile-tag">${escapeHtmlText(label)}</span>`;
                })
            ).join('');

            return `
                <div class="profile-hero">
                    ${heroInner}
                    <div class="profile-hero-overlay">
                        <h2 class="profile-name">${escapeHtmlText(venue.name)}</h2>
                        <p class="profile-address">${escapeHtmlText(venue.address)}</p>
                    </div>
                </div>
                <div class="profile-content">
                    <div class="profile-actions">${actions.join('')}</div>
                    <div class="profile-section"><p class="profile-description">${escapeHtmlText(getVenueText(venue, 'description'))}</p></div>
                    <div class="profile-section">
                        <div class="profile-info-row"><span class="profile-info-label">${translate('popup.hours', 'Hours')}</span><span class="profile-info-value">${formatHoursLines(getVenueText(venue, 'hours'))}</span></div>
                        ${seasonalNote ? `<div class="profile-info-row"><span class="profile-info-label">${ps('note')}</span><span class="profile-info-value seasonal">${escapeHtmlText(seasonalNote)}</span></div>` : ''}
                        <div class="profile-info-row"><span class="profile-info-label">${translate('popup.specialty', 'Specialty')}</span><span class="profile-info-value">${escapeHtmlText(getVenueText(venue, 'specialty'))}</span></div>
                    </div>
                    ${tags ? `<div class="profile-section"><h3 class="profile-section-title">${ps('features')}</h3><div class="profile-tags">${tags}</div></div>` : ''}
                </div>`;
        }

        function refreshActiveMarker() {
            markers.forEach(m => {
                const el = m.marker.getElement();
                if (el) el.classList.toggle('marker-active', m.venue === activeVenue);
            });
        }

        function panMarkerIntoView(latlng) {
            if (isMobile()) {
                // keep the marker in the strip of map left visible above the sheet
                const point = map.latLngToContainerPoint(latlng);
                const targetY = map.getSize().y * 0.18;
                map.panBy([0, point.y - targetY], { animate: true });
            } else {
                map.panInside(latlng, { padding: [70, 70], animate: true });
            }
        }

        function openProfile(venue, source = 'unknown') {
            if (!venue) return;
            activeVenue = venue;
            sliderIndices['profile-slider'] = 0;
            profileScroll.innerHTML = createProfileContent(venue);
            profileScroll.scrollTop = 0;
            profilePanel.classList.add('open');
            profilePanel.classList.remove('full');
            profilePanel.setAttribute('aria-hidden', 'false');
            attachSliderScrollSync(profileScroll.querySelector('.slider-container'));
            refreshActiveMarker();
            if (isMobile()) {
                closeFilterSheet(true);
                sheetBackdrop.classList.add('visible');
            }
            setTimeout(() => panMarkerIntoView(L.latLng(venue.fallbackCoords)), 60);
            trackEvent('profile_open', { ...getVenueAnalyticsParams(venue), source });
        }

        function closeProfile() {
            if (!profilePanel.classList.contains('open')) return;
            profilePanel.classList.remove('open', 'full');
            profilePanel.setAttribute('aria-hidden', 'true');
            activeVenue = null;
            refreshActiveMarker();
            if (isMobile() && !sidebar.classList.contains('show')) sheetBackdrop.classList.remove('visible');
        }

        profileClose.addEventListener('click', closeProfile);
        document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeProfile(); });
        sheetBackdrop.addEventListener('click', closeProfile);
        map.on('click', closeProfile);

        // Mobile sheet gestures: tap the handle to expand/collapse, drag down to dismiss.
        let sheetDragStartY = null;
        profileGrabber.addEventListener('touchstart', (e) => { sheetDragStartY = e.touches[0].clientY; }, { passive: true });
        profileGrabber.addEventListener('touchmove', (e) => {
            if (sheetDragStartY === null) return;
            const delta = e.touches[0].clientY - sheetDragStartY;
            if (delta > 90) { sheetDragStartY = null; closeProfile(); }
            else if (delta < -60) { sheetDragStartY = null; profilePanel.classList.add('full'); }
        }, { passive: true });
        profileGrabber.addEventListener('touchend', () => { sheetDragStartY = null; });
        profileGrabber.addEventListener('click', () => profilePanel.classList.toggle('full'));
        profileScroll.addEventListener('click', (e) => {
            if (isMobile() && e.target.closest('.profile-hero') && !e.target.closest('.slider-arrow')) profilePanel.classList.toggle('full');
        });

        // Initialize
        async function startApp() {"""
replace_once("\n        // Initialize\n        async function startApp() {", PROFILE_JS, "profile js")

io.open(path, 'w', encoding='utf-8', newline='').write(s)
print("patched", path)
