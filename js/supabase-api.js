/**
 * Supabase 직접 연결 API 모듈 (정규화된 스키마 v2)
 * CONFIG.API_MODE='supabase'일 때 사용
 * 
 * 테이블 구조:
 * - companies, certificate_types: 참조 테이블
 * - personnel, certificates, sites: 주요 테이블 (UUID PK, FK 관계)
 * - site_assignments, certificate_assignments: 배정 관계 테이블 (N:M)
 */
const SupabaseAPI = {
    _client: null,

    // Supabase 클라이언트 초기화
    _getClient() {
        if (this._client) return this._client;
        
        if (typeof window !== 'undefined' && window.supabase) {
            this._client = window.supabase.createClient(CONFIG.SUPABASE_URL, CONFIG.SUPABASE_ANON_KEY);
        } else if (typeof window !== 'undefined' && window.supabaseClient) {
            this._client = window.supabaseClient;
        }
        
        if (!this._client) {
            console.error('Supabase 클라이언트를 찾을 수 없습니다.');
        }
        return this._client;
    },

    // === 현장 (Sites) ===
    async getSites(filters = {}) {
        const client = this._getClient();
        if (!client) return null;

        UI.showLoading();
        try {
            // JOIN으로 회사명, 배정 정보 가져오기
            let query = client.from('sites').select(`
                *,
                company:companies(id, name, short_name),
                assignments:site_assignments(
                    id, role, status,
                    personnel:personnel(id, name, phone)
                ),
                cert_assignments:certificate_assignments(
                    id, status,
                    certificate:certificates(id, cert_number, cert_type:certificate_types(name), personnel:personnel(name, phone))
                )
            `);
            
            if (filters.company) {
                // 회사명으로 필터 (short_name 또는 name)
                const { data: company } = await client.from('companies')
                    .select('id')
                    .or(`name.eq.${filters.company},short_name.eq.${filters.company}`)
                    .single();
                if (company) query = query.eq('company_id', company.id);
            }
            if (filters.status) {
                query = query.eq('assignment_status', filters.status);
            }
            if (filters.state) {
                query = query.eq('status', filters.state);
            }
            
            const { data, error } = await query.order('created_at', { ascending: false });
            UI.hideLoading();
            
            if (error) {
                UI.showToast(error.message, 'error');
                return null;
            }
            
            // 프론트엔드 호환용 데이터 변환
            const transformed = (data || []).map(site => this._transformSite(site));
            return { data: transformed, count: transformed.length };
        } catch (err) {
            UI.hideLoading();
            UI.showToast(err.message || '네트워크 오류', 'error');
            return null;
        }
    },

    // 현장 데이터 변환 (프론트엔드 호환)
    _transformSite(site) {
        const activeAssignment = site.assignments?.find(a => a.status === '배정중');
        const activeCertAssignment = site.cert_assignments?.find(a => a.status === '배정중');
        
        return {
            id: site.id,
            '현장ID': site.legacy_id || site.id,
            '현장명': site.name,
            '건축주명': site.owner_name || '',
            '회사구분': site.company?.name || '',
            '주소': site.address || '',
            '위도': site.latitude?.toString() || '',
            '경도': site.longitude?.toString() || '',
            '건축허가일': site.permit_date || '',
            '착공예정일': site.start_date || '',
            '준공일': site.end_date || '',
            '현장상태': site.status || '건축허가',
            '특이사항': site.notes || '',
            '담당소장ID': activeAssignment?.personnel?.id || '',
            '담당소장명': activeAssignment?.personnel?.name || '',
            '담당소장연락처': activeAssignment?.personnel?.phone || '',
            '사용자격증ID': activeCertAssignment?.certificate?.id || '',
            '자격증명': activeCertAssignment?.certificate?.cert_type?.name || '',
            '자격증소유자명': activeCertAssignment?.certificate?.personnel?.name || '',
            '자격증소유자연락처': activeCertAssignment?.certificate?.personnel?.phone || '',
            '배정상태': site.assignment_status || '미배정',
            '등록일': site.created_at?.split('T')[0] || '',
            '수정일': site.updated_at?.split('T')[0] || '',
            // 원본 데이터
            _raw: site
        };
    },

    async searchSites(query) {
        if (!(query && String(query).trim())) {
            return this.getSites({});
        }
        
        const client = this._getClient();
        if (!client) return null;

        UI.showLoading();
        try {
            const searchTerm = query.trim();
            const { data, error } = await client
                .from('sites')
                .select(`
                    *,
                    company:companies(id, name, short_name),
                    assignments:site_assignments(id, role, status, personnel:personnel(id, name, phone)),
                    cert_assignments:certificate_assignments(id, status, certificate:certificates(id, cert_type:certificate_types(name), personnel:personnel(name, phone)))
                `)
                .or(`name.ilike.%${searchTerm}%,address.ilike.%${searchTerm}%,owner_name.ilike.%${searchTerm}%`);
            
            UI.hideLoading();
            if (error) {
                UI.showToast(error.message, 'error');
                return null;
            }
            const transformed = (data || []).map(site => this._transformSite(site));
            return { data: transformed, count: transformed.length };
        } catch (err) {
            UI.hideLoading();
            UI.showToast(err.message || '네트워크 오류', 'error');
            return null;
        }
    },

    async getSiteDetail(siteId) {
        const client = this._getClient();
        if (!client) return null;

        UI.showLoading();
        try {
            const { data, error } = await client
                .from('sites')
                .select(`
                    *,
                    company:companies(id, name, short_name),
                    assignments:site_assignments(id, role, status, personnel:personnel(id, legacy_id, name, phone)),
                    cert_assignments:certificate_assignments(id, status, certificate:certificates(id, legacy_id, cert_number, cert_type:certificate_types(name), personnel:personnel(name, phone)))
                `)
                .or(`id.eq.${siteId},legacy_id.eq.${siteId}`)
                .single();
            
            UI.hideLoading();
            if (error) {
                UI.showToast(error.message, 'error');
                return null;
            }
            return this._transformSite(data);
        } catch (err) {
            UI.hideLoading();
            UI.showToast(err.message || '네트워크 오류', 'error');
            return null;
        }
    },

    async createSite(siteData) {
        const client = this._getClient();
        if (!client) return null;

        UI.showLoading();
        try {
            // 회사 ID 조회
            let companyId = null;
            if (siteData['회사구분'] || siteData.company) {
                const companyName = siteData['회사구분'] || siteData.company;
                const { data: company } = await client.from('companies')
                    .select('id')
                    .or(`name.eq.${companyName},short_name.eq.${companyName}`)
                    .single();
                companyId = company?.id;
            }

            const insertData = {
                legacy_id: siteData['현장ID'] || null,
                company_id: companyId,
                name: siteData['현장명'] || siteData.name,
                owner_name: siteData['건축주명'] || '',
                address: siteData['주소'] || siteData.address,
                latitude: siteData['위도'] ? parseFloat(siteData['위도']) : null,
                longitude: siteData['경도'] ? parseFloat(siteData['경도']) : null,
                permit_date: siteData['건축허가일'] || null,
                start_date: siteData['착공예정일'] || null,
                end_date: siteData['준공일'] || null,
                status: siteData['현장상태'] || '건축허가',
                assignment_status: '미배정',
                notes: siteData['특이사항'] || ''
            };

            const { data, error } = await client.from('sites').insert([insertData]).select().single();
            
            UI.hideLoading();
            if (error) {
                UI.showToast(error.message, 'error');
                return null;
            }
            return { success: true, data: this._transformSite(data) };
        } catch (err) {
            UI.hideLoading();
            UI.showToast(err.message || '네트워크 오류', 'error');
            return null;
        }
    },

    async updateSite(siteId, updateData) {
        const client = this._getClient();
        if (!client) return null;

        UI.showLoading();
        try {
            const updateObj = {
                updated_at: new Date().toISOString()
            };
            
            if (updateData['현장명']) updateObj.name = updateData['현장명'];
            if (updateData['주소']) updateObj.address = updateData['주소'];
            if (updateData['위도']) updateObj.latitude = parseFloat(updateData['위도']);
            if (updateData['경도']) updateObj.longitude = parseFloat(updateData['경도']);
            if (updateData['건축허가일']) updateObj.permit_date = updateData['건축허가일'];
            if (updateData['착공예정일']) updateObj.start_date = updateData['착공예정일'];
            if (updateData['준공일']) updateObj.end_date = updateData['준공일'];
            if (updateData['현장상태']) updateObj.status = updateData['현장상태'];
            if (updateData['특이사항'] !== undefined) updateObj.notes = updateData['특이사항'];

            const { data, error } = await client
                .from('sites')
                .update(updateObj)
                .or(`id.eq.${siteId},legacy_id.eq.${siteId}`)
                .select()
                .single();
            
            UI.hideLoading();
            if (error) {
                UI.showToast(error.message, 'error');
                return null;
            }
            return { success: true, data };
        } catch (err) {
            UI.hideLoading();
            UI.showToast(err.message || '네트워크 오류', 'error');
            return null;
        }
    },

    async assignManager(siteId, assignData) {
        const client = this._getClient();
        if (!client) return null;

        UI.showLoading();
        try {
            // 현장 UUID 조회
            const { data: site } = await client.from('sites')
                .select('id')
                .or(`id.eq.${siteId},legacy_id.eq.${siteId}`)
                .single();
            if (!site) throw new Error('현장을 찾을 수 없습니다.');

            // 인력 배정
            if (assignData.담당소장ID || assignData.manager_id) {
                const personnelId = assignData.담당소장ID || assignData.manager_id;
                const { data: personnel } = await client.from('personnel')
                    .select('id')
                    .or(`id.eq.${personnelId},legacy_id.eq.${personnelId}`)
                    .single();
                
                if (personnel) {
                    await client.from('site_assignments').insert({
                        site_id: site.id,
                        personnel_id: personnel.id,
                        role: '담당',
                        status: '배정중'
                    });
                }
            }

            // 자격증 배정
            if (assignData.사용자격증ID || assignData.certificate_id) {
                const certId = assignData.사용자격증ID || assignData.certificate_id;
                const { data: cert } = await client.from('certificates')
                    .select('id')
                    .or(`id.eq.${certId},legacy_id.eq.${certId}`)
                    .single();
                
                if (cert) {
                    await client.from('certificate_assignments').insert({
                        certificate_id: cert.id,
                        site_id: site.id,
                        status: '배정중'
                    });
                    // 자격증 상태 업데이트
                    await client.from('certificates').update({ status: '사용중' }).eq('id', cert.id);
                }
            }

            // 현장 배정상태 업데이트
            await client.from('sites').update({
                assignment_status: '배정완료',
                updated_at: new Date().toISOString()
            }).eq('id', site.id);
            
            UI.hideLoading();
            return { success: true };
        } catch (err) {
            UI.hideLoading();
            UI.showToast(err.message || '네트워크 오류', 'error');
            return null;
        }
    },

    async unassignManager(siteId) {
        const client = this._getClient();
        if (!client) return null;

        UI.showLoading();
        try {
            // 현장 UUID 조회
            const { data: site } = await client.from('sites')
                .select('id')
                .or(`id.eq.${siteId},legacy_id.eq.${siteId}`)
                .single();
            if (!site) throw new Error('현장을 찾을 수 없습니다.');

            // 자격증 배정 해제 → 자격증 상태 복원
            const { data: certAssignments } = await client.from('certificate_assignments')
                .select('certificate_id')
                .eq('site_id', site.id)
                .eq('status', '배정중');
            
            for (const ca of (certAssignments || [])) {
                await client.from('certificates').update({ status: '사용가능' }).eq('id', ca.certificate_id);
            }

            // 배정 관계 해제
            await client.from('site_assignments')
                .update({ status: '해제', released_at: new Date().toISOString() })
                .eq('site_id', site.id)
                .eq('status', '배정중');
            
            await client.from('certificate_assignments')
                .update({ status: '해제', released_at: new Date().toISOString() })
                .eq('site_id', site.id)
                .eq('status', '배정중');

            // 현장 상태 업데이트
            await client.from('sites').update({
                assignment_status: '미배정',
                updated_at: new Date().toISOString()
            }).eq('id', site.id);
            
            UI.hideLoading();
            return { success: true };
        } catch (err) {
            UI.hideLoading();
            UI.showToast(err.message || '네트워크 오류', 'error');
            return null;
        }
    },

    // === 인력 (Personnel) ===
    async getPersonnel(filters = {}) {
        const client = this._getClient();
        if (!client) return null;

        UI.showLoading();
        try {
            let query = client.from('personnel').select(`
                *,
                company:companies(id, name, short_name)
            `);
            
            if (filters.status) {
                query = query.eq('status', filters.status);
            }
            if (filters.role) {
                query = query.eq('position', filters.role);
            }
            
            const { data, error } = await query;
            UI.hideLoading();
            
            if (error) {
                UI.showToast(error.message, 'error');
                return null;
            }
            
            // 프론트엔드 호환 변환
            const transformed = (data || []).map(p => ({
                id: p.id,
                '인력ID': p.legacy_id || p.id,
                '성명': p.name,
                '직책': p.position || '',
                '소속': p.company?.name || '',
                '연락처': p.phone || '',
                '이메일': p.email || '',
                '현재상태': p.status || '투입가능',
                '현재담당현장수': p.current_site_count || 0,
                '비고': p.notes || '',
                '입사일': p.join_date || '',
                _raw: p
            }));
            return { data: transformed, count: transformed.length };
        } catch (err) {
            UI.hideLoading();
            UI.showToast(err.message || '네트워크 오류', 'error');
            return null;
        }
    },

    async getPersonnelDetail(personId) {
        const client = this._getClient();
        if (!client) return null;

        UI.showLoading();
        try {
            const { data, error } = await client
                .from('personnel')
                .select(`*, company:companies(id, name, short_name)`)
                .or(`id.eq.${personId},legacy_id.eq.${personId}`)
                .single();
            
            UI.hideLoading();
            if (error) {
                UI.showToast(error.message, 'error');
                return null;
            }
            return {
                id: data.id,
                '인력ID': data.legacy_id || data.id,
                '성명': data.name,
                '직책': data.position || '',
                '소속': data.company?.name || '',
                '연락처': data.phone || '',
                '이메일': data.email || '',
                '현재상태': data.status || '투입가능',
                '현재담당현장수': data.current_site_count || 0,
                '비고': data.notes || '',
                _raw: data
            };
        } catch (err) {
            UI.hideLoading();
            UI.showToast(err.message || '네트워크 오류', 'error');
            return null;
        }
    },

    // === 자격증 (Certificates) ===
    async getCertificates(filters = {}) {
        const client = this._getClient();
        if (!client) return null;

        UI.showLoading();
        try {
            let query = client.from('certificates').select(`
                *,
                cert_type:certificate_types(id, name),
                personnel:personnel(id, name, phone)
            `);
            
            if (filters.available === true || filters.available === 'true') {
                query = query.eq('status', '사용가능');
            } else if (filters.available === false || filters.available === 'false') {
                query = query.neq('status', '사용가능');
            }
            
            const { data, error } = await query;
            UI.hideLoading();
            
            if (error) {
                UI.showToast(error.message, 'error');
                return null;
            }
            
            const transformed = (data || []).map(c => ({
                id: c.id,
                '자격증ID': c.legacy_id || c.id,
                '자격증명': c.cert_type?.name || '',
                '자격증번호': c.cert_number || '',
                '소유자ID': c.personnel?.id || '',
                '소유자명': c.personnel?.name || '',
                '소유자연락처': c.personnel?.phone || '',
                '취득일': c.issued_date || '',
                '유효기간': c.expiry_date || '',
                '사용가능여부': c.status || '사용가능',
                '비고': c.notes || '',
                _raw: c
            }));
            return { data: transformed, count: transformed.length };
        } catch (err) {
            UI.hideLoading();
            UI.showToast(err.message || '네트워크 오류', 'error');
            return null;
        }
    },

    async getCertificateDetail(certId) {
        const client = this._getClient();
        if (!client) return null;

        UI.showLoading();
        try {
            const { data, error } = await client
                .from('certificates')
                .select(`*, cert_type:certificate_types(name), personnel:personnel(id, name, phone)`)
                .or(`id.eq.${certId},legacy_id.eq.${certId}`)
                .single();
            
            UI.hideLoading();
            if (error) {
                UI.showToast(error.message, 'error');
                return null;
            }
            return {
                id: data.id,
                '자격증ID': data.legacy_id || data.id,
                '자격증명': data.cert_type?.name || '',
                '자격증번호': data.cert_number || '',
                '소유자ID': data.personnel?.id || '',
                '소유자명': data.personnel?.name || '',
                '소유자연락처': data.personnel?.phone || '',
                '취득일': data.issued_date || '',
                '유효기간': data.expiry_date || '',
                '사용가능여부': data.status || '사용가능',
                '비고': data.notes || '',
                _raw: data
            };
        } catch (err) {
            UI.hideLoading();
            UI.showToast(err.message || '네트워크 오류', 'error');
            return null;
        }
    },

    async createCertificate(certData) {
        const client = this._getClient();
        if (!client) return null;

        UI.showLoading();
        try {
            // 자격증 종류 ID 조회
            let certTypeId = null;
            if (certData['자격증명']) {
                const { data: certType } = await client.from('certificate_types')
                    .select('id')
                    .eq('name', certData['자격증명'])
                    .single();
                certTypeId = certType?.id;
            }

            // 소유자 ID 조회 (이름으로)
            let personnelId = null;
            if (certData['소유자명']) {
                const { data: personnel } = await client.from('personnel')
                    .select('id')
                    .eq('name', certData['소유자명'])
                    .single();
                personnelId = personnel?.id;
            }

            const insertData = {
                legacy_id: certData['자격증ID'] || null,
                cert_type_id: certTypeId,
                personnel_id: personnelId,
                cert_number: certData['자격증번호'] || '',
                issued_date: certData['취득일'] || null,
                expiry_date: certData['유효기간'] || null,
                status: certData['사용가능여부'] || '사용가능',
                notes: certData['비고'] || ''
            };

            const { data, error } = await client.from('certificates').insert([insertData]).select().single();
            
            UI.hideLoading();
            if (error) {
                UI.showToast(error.message, 'error');
                return null;
            }
            return { success: true, data };
        } catch (err) {
            UI.hideLoading();
            UI.showToast(err.message || '네트워크 오류', 'error');
            return null;
        }
    },

    // === 통계 ===
    async getStats() {
        const client = this._getClient();
        if (!client) return null;

        UI.showLoading();
        try {
            const [sitesRes, personnelRes, certsRes] = await Promise.all([
                client.from('sites').select('status, assignment_status, company_id'),
                client.from('personnel').select('status'),
                client.from('certificates').select('status')
            ]);
            
            UI.hideLoading();
            
            const sites = sitesRes.data || [];
            const personnel = personnelRes.data || [];
            const certificates = certsRes.data || [];
            
            return {
                sites: {
                    total: sites.length,
                    assigned: sites.filter(s => s.assignment_status === '배정완료').length,
                    unassigned: sites.filter(s => s.assignment_status === '미배정').length,
                    byStatus: sites.reduce((acc, s) => {
                        acc[s.status] = (acc[s.status] || 0) + 1;
                        return acc;
                    }, {}),
                    byCompany: {}
                },
                personnel: {
                    total: personnel.length,
                    available: personnel.filter(p => p.status === '투입가능').length,
                    deployed: personnel.filter(p => p.status === '투입중').length
                },
                certificates: {
                    total: certificates.length,
                    available: certificates.filter(c => c.status === '사용가능').length,
                    inUse: certificates.filter(c => c.status === '사용중').length
                }
            };
        } catch (err) {
            UI.hideLoading();
            UI.showToast(err.message || '네트워크 오류', 'error');
            return null;
        }
    },

    // === 헬스 체크 ===
    async healthCheck() {
        const client = this._getClient();
        if (!client) return false;
        
        try {
            const { error } = await client.from('sites').select('count', { count: 'exact', head: true });
            return !error;
        } catch {
            return false;
        }
    }
};
