# Friendly Spaces web-map analytics

The embedded map sends interaction events to the Friendly Spaces Website (Wix)
GA4 stream, measurement ID `G-N294L2D9QJ`. It does not send a second automatic
`page_view`; the Wix parent page remains responsible for page views and sessions.

The map starts GA4 in consent mode with analytics storage denied. This supports
aggregate, cookieless measurement without placing an analytics cookie from the
cross-origin GitHub Pages iframe. It also posts the same event payload to the Wix
parent with `source: friendly-spaces-map`, ready for a future Wix/Velo consent
bridge if consented, cookie-based measurement is required.

## Events

| Event | Trigger |
| --- | --- |
| `map_view` | Venue data has loaded and the map is ready |
| `profile_open` | A Friendly Space marker popup opens |
| `filter_use` | A filter is selected or deselected |
| `filters_clear` | Filters/search are cleared |
| `search_use` | A search is submitted, selected, or paused after typing |
| `search_zero_results` | A tracked search has no matching venues |
| `directions_click` | The venue address/directions link is opened |
| `call_click` | A venue telephone link is selected |
| `website_click` | A venue website is opened |
| `instagram_click` | A venue Instagram profile is opened |

Venue events include `partner_id`, `partner_name`, `partner_city`,
`partner_category`, `surface` (`web_map`) and `map_language`. The stable
`partner_id` comes from the shared venue JSON `slug` field.

Filter events include `filter_category`, `filter_value`, `filter_state`,
`active_filter_count` and `visible_venues`. Search events include a sanitized
`search_term`, `search_method`, `search_results` and `active_filter_count`.

Add `?analytics_debug=1` to the standalone map URL when verifying events in GA4
DebugView. This adds `debug_mode: true` to emitted events.
