/**
 * Kakao Maps API 연동 - SiteMap
 * CONFIG.KAKAO_APP_KEY 설정 시 Kakao 지도 사용, 미설정 시 캔버스 폴백
 */
const SiteMap = {
    map: null,
    markers: [],
    clusterer: null,
    geocoder: null,
    container: null,
    infoOverlay: null,
    siteData: null,
    canvasFallback: { canvas: null, ctx: null, markers: [] },
    initRetryCount: 0,
    MAX_INIT_RETRY: 50,

    init(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) return;

        if (typeof kakao === 'undefined' || !kakao.maps) {
            if (this.initRetryCount < this.MAX_INIT_RETRY) {
                this.initRetryCount++;
                setTimeout(() => this.init(containerId), 100);
                return;
            }
            this._initCanvasFallback();
            return;
        }

        var self = this;
        kakao.maps.load(function() {
            self._initKakaoMap();
        });
    },

    _initKakaoMap() {
        if (!this.container) return;
        var center = CONFIG.MAP_CENTER || { lat: 37.0, lng: 127.0 };
        var level = CONFIG.MAP_ZOOM != null ? CONFIG.MAP_ZOOM : 9;
        var latlng = new kakao.maps.LatLng(center.lat, center.lng);

        this.container.innerHTML = '';
        var mapOption = { center: latlng, level: level };
        this.map = new kakao.maps.Map(this.container, mapOption);

        var zoomControl = new kakao.maps.ZoomControl();
        this.map.addControl(zoomControl, kakao.maps.ControlPosition.RIGHT);

        var mapTypeControl = new kakao.maps.MapTypeControl();
        this.map.addControl(mapTypeControl, kakao.maps.ControlPosition.TOPRIGHT);

        this.geocoder = new kakao.maps.services.Geocoder();
        this._createInfoOverlay();
        if (this.siteData) this.updateMarkers(this.siteData);
    },

    _createInfoOverlay() {
        var wrap = document.createElement('div');
        wrap.className = 'kakao-info-overlay';
        wrap.style.cssText = 'display:none; position:absolute; padding:10px 12px; background:rgba(30,30,40,0.95); color:#e0e0e0; border-radius:8px; font-size:13px; box-shadow:0 4px 12px rgba(0,0,0,0.4); border:1px solid #3498db; min-width:160px; z-index:10;';
        wrap.innerHTML = '<div class="info-title" style="font-weight:bold; margin-bottom:6px; color:#3498db;"></div><div class="info-company" style="margin-bottom:4px;"></div><div class="info-manager" style="font-size:12px; color:#95a5a6;"></div>';
        this.container.appendChild(wrap);
        this.infoOverlayEl = wrap;
    },

    _showInfoOverlay(position, site) {
        if (!this.infoOverlayEl) return;
        var name = site['현장명'] || site.name || '정보 없음';
        var company = DISPLAY_MAP.company[site['회사구분'] || site.company] || (site['회사구분'] || site.company || '-');
        var manager = site['담당소장명'] || site.manager || '미배정';
        this.infoOverlayEl.querySelector('.info-title').textContent = name;
        this.infoOverlayEl.querySelector('.info-company').textContent = '회사: ' + company;
        this.infoOverlayEl.querySelector('.info-manager').textContent = '담당: ' + manager;
        this.infoOverlayEl.style.display = 'block';
        var proj = this.map.getProjection();
        var point = proj.pointFromCoords(position);
        this.infoOverlayEl.style.left = (point.x + 15) + 'px';
        this.infoOverlayEl.style.top = (point.y - 10) + 'px';
    },

    _hideInfoOverlay() {
        if (this.infoOverlayEl) this.infoOverlayEl.style.display = 'none';
    },

    _clearMarkers() {
        this.markers.forEach(function(m) {
            if (m.overlay && m.overlay.setMap) m.overlay.setMap(null);
        });
        this.markers = [];
        if (this.clusterer && this.clusterer.clear) this.clusterer.clear();
    },

    _getMarkerColor(site) {
        var status = site['배정상태'] || site.status || '미배정';
        return DISPLAY_MAP.statusColor[status] || '#95a5a6';
    },

    _createMarkerOverlay(position, site, isUnassigned) {
        var color = this._getMarkerColor(site);
        var div = document.createElement('div');
        div.className = 'kakao-marker-pin' + (isUnassigned ? ' unassigned-pulse' : '');
        div.style.cssText = 'width:28px; height:28px; border-radius:50%; background:' + color + '; border:2px solid #fff; box-shadow:0 2px 6px rgba(0,0,0,0.3); cursor:pointer;';
        var self = this;
        div.addEventListener('click', function(ev) {
            ev.stopPropagation();
            var id = site['현장ID'] || site.id;
            if (id && typeof SiteDetail !== 'undefined') SiteDetail.open(id);
        });
        div.addEventListener('mouseenter', function() {
            self._showInfoOverlay(position, site);
        });
        div.addEventListener('mouseleave', function() {
            self._hideInfoOverlay();
        });

        var overlay = new kakao.maps.CustomOverlay({
            position: position,
            content: div,
            yAnchor: 0.5,
            xAnchor: 0.5
        });
        return overlay;
    },

    _addMarker(site, lat, lng) {
        if (!this.map) return null;
        var position = new kakao.maps.LatLng(lat, lng);
        var status = site['배정상태'] || site.status || '미배정';
        var isUnassigned = status === '미배정';
        var overlay = this._createMarkerOverlay(position, site, isUnassigned);
        overlay.setMap(this.map);
        this.markers.push({ site: site, overlay: overlay, position: position });
        return overlay;
    },

    updateMarkers(sites) {
        this.siteData = sites;
        if (!sites || !sites.length) {
            this._clearMarkers();
            if (this._isCanvasFallback()) this._updateCanvasMarkers([]);
            return;
        }

        if (this._isCanvasFallback()) {
            this._updateCanvasMarkers(sites);
            return;
        }

        if (!this.map) return;

        this._clearMarkers();
        var self = this;
        var withCoord = [];
        var withoutCoord = [];

        sites.forEach(function(site) {
            var lat = parseFloat(site['위도']) || parseFloat(site.lat);
            var lng = parseFloat(site['경도']) || parseFloat(site.lng);
            if (!isNaN(lat) && !isNaN(lng)) withCoord.push({ site: site, lat: lat, lng: lng });
            else if (site['주소'] || site.address) withoutCoord.push(site);
        });

        withCoord.forEach(function(item) {
            self._addMarker(item.site, item.lat, item.lng);
        });

        if (withoutCoord.length > 0 && this.geocoder) {
            withoutCoord.forEach(function(site) {
                var addr = site['주소'] || site.address || '';
                if (!addr) return;
                self.geocoder.addressSearch(addr, function(result, status) {
                    if (status === kakao.maps.services.Status.OK && result && result[0]) {
                        var lat = parseFloat(result[0].y);
                        var lng = parseFloat(result[0].x);
                        if (!isNaN(lat) && !isNaN(lng)) self._addMarker(site, lat, lng);
                    }
                });
            });
        }

        /* MarkerClusterer는 kakao.maps.Marker 전용. CustomOverlay 마커 사용 시 생략 */
    },

    _isCanvasFallback() {
        return this.canvasFallback.canvas != null;
    },

    _initCanvasFallback() {
        if (!this.container) return;
        this.container.innerHTML = '';
        if (typeof CONFIG !== 'undefined' && !CONFIG.KAKAO_APP_KEY) {
            var msg = document.createElement('div');
            msg.className = 'map-fallback-msg';
            msg.style.cssText = 'position:absolute; top:12px; left:12px; padding:8px 12px; background:rgba(30,30,40,0.9); color:#95a5a6; font-size:12px; border-radius:6px; z-index:5;';
            msg.textContent = 'Kakao Maps 사용 시 config.js에 KAKAO_APP_KEY를 설정하세요.';
            this.container.appendChild(msg);
        }
        var canvas = document.createElement('canvas');
        canvas.id = 'mapCanvas';
        canvas.style.cssText = 'width:100%; height:100%; display:block;';
        this.container.appendChild(canvas);
        this.canvasFallback.canvas = canvas;
        this.canvasFallback.ctx = canvas.getContext('2d');
        var self = this;
        window.addEventListener('resize', function() { self._resizeCanvas(); });
        canvas.addEventListener('click', function(e) { self._handleCanvasClick(e); });
        this._resizeCanvas();
        if (this.siteData) this.updateMarkers(this.siteData);
    },

    _resizeCanvas() {
        var c = this.canvasFallback.canvas;
        var container = this.container;
        if (!c || !container) return;
        var w = container.offsetWidth;
        var h = container.offsetHeight;
        c.width = w;
        c.height = h;
        this._drawCanvas();
    },

    _drawCanvas() {
        var ctx = this.canvasFallback.ctx;
        var canvas = this.canvasFallback.canvas;
        var markers = this.canvasFallback.markers;
        if (!ctx || !canvas) return;
        var w = canvas.width;
        var h = canvas.height;
        ctx.fillStyle = '#1a1a2e';
        ctx.fillRect(0, 0, w, h);
        for (var i = 0; i < w; i += 40) {
            ctx.strokeStyle = '#2a2a4e';
            ctx.beginPath();
            ctx.moveTo(i, 0);
            ctx.lineTo(i, h);
            ctx.stroke();
        }
        for (var i = 0; i < h; i += 40) {
            ctx.beginPath();
            ctx.moveTo(0, i);
            ctx.lineTo(w, i);
            ctx.stroke();
        }
        markers.forEach(function(m) {
            ctx.fillStyle = m.color;
            ctx.beginPath();
            ctx.arc(m.x, m.y, m.radius, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#fff';
            ctx.font = 'bold 10px sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(m.status === '미배정' ? '!' : '✓', m.x, m.y);
        });
    },

    _updateCanvasMarkers(sites) {
        var markers = this.canvasFallback.markers = [];
        if (!sites || !sites.length) {
            this._drawCanvas();
            return;
        }
        var withCoord = sites.filter(function(s) {
            var lat = parseFloat(s['위도']) || parseFloat(s.lat);
            var lng = parseFloat(s['경도']) || parseFloat(s.lng);
            return !isNaN(lat) && !isNaN(lng);
        });
        if (withCoord.length === 0) {
            this._drawCanvas();
            return;
        }
        var lats = withCoord.map(function(s) { return parseFloat(s['위도']) || parseFloat(s.lat); });
        var lngs = withCoord.map(function(s) { return parseFloat(s['경도']) || parseFloat(s.lng); });
        var minLat = Math.min.apply(null, lats);
        var maxLat = Math.max.apply(null, lats);
        var minLng = Math.min.apply(null, lngs);
        var maxLng = Math.max.apply(null, lngs);
        var pad = 50;
        var w = this.canvasFallback.canvas ? this.canvasFallback.canvas.width : 400;
        var h = this.canvasFallback.canvas ? this.canvasFallback.canvas.height : 300;
        var rangeLng = maxLng - minLng || 0.01;
        var rangeLat = maxLat - minLat || 0.01;
        var self = this;
        withCoord.forEach(function(site) {
            var lat = parseFloat(site['위도']) || parseFloat(site.lat);
            var lng = parseFloat(site['경도']) || parseFloat(site.lng);
            var x = pad + ((lng - minLng) / rangeLng) * (w - pad * 2);
            var y = h - pad - ((lat - minLat) / rangeLat) * (h - pad * 2);
            var status = site['배정상태'] || site.status || '미배정';
            var color = DISPLAY_MAP.statusColor[status] || '#95a5a6';
            markers.push({ site: site, x: x, y: y, radius: 8, color: color, status: status });
        });
        this._drawCanvas();
    },

    _handleCanvasClick(event) {
        var canvas = this.canvasFallback.canvas;
        if (!canvas) return;
        var rect = canvas.getBoundingClientRect();
        var x = event.clientX - rect.left;
        var y = event.clientY - rect.top;
        var markers = this.canvasFallback.markers;
        for (var i = markers.length - 1; i >= 0; i--) {
            var m = markers[i];
            var dist = Math.hypot(x - m.x, y - m.y);
            if (dist <= m.radius + 5 && typeof SiteDetail !== 'undefined') {
                SiteDetail.open(m.site['현장ID'] || m.site.id);
                break;
            }
        }
    },

    focusSite(lat, lng) {
        if (this.map) {
            var latlng = new kakao.maps.LatLng(lat, lng);
            this.map.setCenter(latlng);
            this.map.setLevel(5);
        } else if (this.canvasFallback.canvas) {
            this._resizeCanvas();
        }
    }
};
