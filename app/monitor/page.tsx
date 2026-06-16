'use client'

import { useEffect, useState } from 'react'
import { sbFetch, sbCount } from '@/lib/supabase'

type SurveillanceMeeting = {
  meeting_id: string
  municipality: string
  county: string
  entity_type: string
  title: string
  meeting_date: string
  meeting_time: string | null
  location: string | null
  agenda_url: string | null
  status: string
  match_count: number
  matched_keywords: string[]
  flagged_items: string[]
}

type Municipality = {
  id: string
  name: string
  county: string
  platform: string
  entity_type: string
  active: boolean
}

const KW_COLORS: Record<string, string> = {
  'Flock Safety':           '#dc2626',
  'Flock camera':           '#dc2626',
  'ALPR':                   '#ea580c',
  'ANPR':                   '#ea580c',
  'ShotSpotter':            '#d97706',
  'gunshot detection':      '#d97706',
  'facial recognition':     '#7c3aed',
  'real-time crime center': '#7c3aed',
  'RTCC':                   '#7c3aed',
  'predictive policing':    '#7c3aed',
  'Palantir':               '#7c3aed',
  'biometric':              '#7c3aed',
  'Axon':                   '#457b9d',
  'Verkada':                '#457b9d',
  'Avigilon':               '#457b9d',
  'Genetec':                '#457b9d',
  'Fusus':                  '#457b9d',
}

function KeywordBadge({ kw }: { kw: string }) {
  return (
    <span style={{
      background: KW_COLORS[kw] ?? '#2a2a3e',
      color: '#fff', fontSize: 11, fontWeight: 700,
      padding: '2px 9px', borderRadius: 4,
      whiteSpace: 'nowrap' as const, letterSpacing: '0.02em',
    }}>{kw}</span>
  )
}

function AlertCard({ meeting }: { meeting: SurveillanceMeeting }) {
  const date      = new Date(meeting.meeting_date + 'T12:00:00')
  const dateStr   = date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })
  const daysUntil = Math.ceil((date.getTime() - Date.now()) / 86400000)
  const isUrgent  = daysUntil >= 0 && daysUntil <= 7
  const isSchool  = meeting.entity_type === 'school_district'

  return (
    <div style={{
      border: `1px solid ${isUrgent ? '#e63946' : '#1e1e2e'}`,
      borderRadius: 12, padding: '18px 20px', marginBottom: 14,
      background: isUrgent ? 'rgba(230,57,70,0.05)' : '#111118',
    }}>
      {/* header row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12, flexWrap: 'wrap' as const }}>
        <div style={{ minWidth: 0, flex: 1 }}>
          <div style={{ fontSize: 11, color: '#7a7a9a', textTransform: 'uppercase' as const, letterSpacing: '0.08em', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>{meeting.county} County · {meeting.municipality}</span>
            {isSchool && (
              <span style={{ background: 'rgba(99,102,241,0.15)', color: '#818cf8', fontSize: 10, fontWeight: 700, padding: '1px 7px', borderRadius: 4, letterSpacing: '0.05em' }}>
                SCHOOL DISTRICT
              </span>
            )}
          </div>
          <div style={{ fontSize: 16, fontWeight: 700, color: '#e8e8f0', marginBottom: 4, lineHeight: 1.3 }}>
            {meeting.title}
          </div>
          <div style={{ fontSize: 13, color: '#7a7a9a' }}>
            {dateStr}{meeting.meeting_time ? ` · ${meeting.meeting_time}` : ''}
            {meeting.location ? ` · ${meeting.location}` : ''}
          </div>
        </div>

        {/* urgency + link stacked */}
        <div style={{ display: 'flex', flexDirection: 'column' as const, alignItems: 'flex-end', gap: 8, flexShrink: 0 }}>
          {daysUntil === 0 && (
            <span style={{ color: '#e63946', fontWeight: 700, fontSize: 12, letterSpacing: '0.06em', textTransform: 'uppercase' as const }}>TODAY</span>
          )}
          {isUrgent && daysUntil > 0 && (
            <span style={{ color: '#e63946', fontWeight: 700, fontSize: 12 }}>⚠ {daysUntil}d away</span>
          )}
          {meeting.agenda_url && (
            <a href={meeting.agenda_url} target="_blank" rel="noopener noreferrer" style={{
              fontSize: 12, color: '#e63946', textDecoration: 'none',
              border: '1px solid #e63946', padding: '5px 12px', borderRadius: 6, fontWeight: 600,
              whiteSpace: 'nowrap' as const,
            }}>View Agenda →</a>
          )}
        </div>
      </div>

      {/* keywords */}
      <div style={{ marginTop: 12, display: 'flex', flexWrap: 'wrap' as const, gap: 6 }}>
        {meeting.matched_keywords?.map(kw => <KeywordBadge key={kw} kw={kw} />)}
      </div>

      {/* flagged items */}
      {meeting.flagged_items?.length > 0 && (
        <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid #1e1e2e' }}>
          <div style={{ fontSize: 11, color: '#7a7a9a', marginBottom: 8, textTransform: 'uppercase' as const, letterSpacing: '0.08em' }}>Flagged Items</div>
          {meeting.flagged_items.slice(0, 3).map((item, i) => (
            <div key={i} style={{ fontSize: 13, color: '#c8c8d8', marginBottom: 6, paddingLeft: 10, borderLeft: '2px solid #1e1e2e', lineHeight: 1.4 }}>
              {item.length > 130 ? item.slice(0, 130) + '…' : item}
            </div>
          ))}
          {meeting.flagged_items.length > 3 && (
            <div style={{ fontSize: 12, color: '#7a7a9a', marginTop: 4 }}>+{meeting.flagged_items.length - 3} more items</div>
          )}
        </div>
      )}
    </div>
  )
}

function EntityTable({ rows, label }: { rows: Municipality[], label: string }) {
  const platformCounts = rows.reduce((acc, m) => {
    acc[m.platform] = (acc[m.platform] ?? 0) + 1
    return acc
  }, {} as Record<string, number>)

  return (
    <div style={{ marginBottom: 48 }}>
      <h2 style={{ fontSize: 17, fontWeight: 800, margin: '0 0 14px', letterSpacing: '-0.01em' }}>
        {label}
        <span style={{ marginLeft: 10, fontSize: 13, color: '#7a7a9a', fontWeight: 400 }}>
          {Object.entries(platformCounts).map(([p, n]) => `${n} ${p}`).join(' · ')}
        </span>
      </h2>
      <div style={{ border: '1px solid #1e1e2e', borderRadius: 12, overflowX: 'auto' as const }}>
        <table className="muni-table" style={{ width: '100%', borderCollapse: 'collapse' as const, fontSize: 13 }}>
          <thead>
            <tr style={{ background: '#111118', borderBottom: '1px solid #1e1e2e' }}>
              {['Name', 'County', 'Platform'].map(h => (
                <th key={h} style={{
                  padding: '10px 16px', textAlign: 'left' as const,
                  color: '#7a7a9a', fontWeight: 700,
                  textTransform: 'uppercase' as const, fontSize: 11, letterSpacing: '0.08em',
                  whiteSpace: 'nowrap' as const,
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((m, i) => (
              <tr key={m.id} style={{
                borderBottom: i < rows.length - 1 ? '1px solid #1e1e2e' : 'none',
                background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)',
              }}>
                <td style={{ padding: '9px 16px', color: '#e8e8f0' }}>{m.name}</td>
                <td style={{ padding: '9px 16px', color: '#7a7a9a', whiteSpace: 'nowrap' as const }}>{m.county}</td>
                <td style={{ padding: '9px 16px' }}>
                  <span style={{
                    fontSize: 11, padding: '2px 8px', borderRadius: 4, fontWeight: 700, letterSpacing: '0.04em',
                    background: m.platform === 'legistar' ? 'rgba(230,57,70,0.12)'
                              : m.platform === 'boarddocs' ? 'rgba(99,102,241,0.12)'
                              : 'rgba(122,122,154,0.12)',
                    color: m.platform === 'legistar' ? '#e63946'
                         : m.platform === 'boarddocs' ? '#818cf8'
                         : '#7a7a9a',
                    whiteSpace: 'nowrap' as const,
                  }}>{m.platform}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [alerts,          setAlerts]          = useState<SurveillanceMeeting[]>([])
  const [municipalities,  setMunicipalities]  = useState<Municipality[]>([])
  const [schoolDistricts, setSchoolDistricts] = useState<Municipality[]>([])
  const [meetingCount,    setMeetingCount]    = useState(0)
  const [loading,         setLoading]         = useState(true)
  const [error,           setError]           = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      sbFetch('surveillance_meetings?select=*&order=meeting_date'),
      sbFetch('municipalities?select=*&entity_type=eq.municipality&order=name'),
      sbFetch('municipalities?select=*&entity_type=eq.school_district&order=name'),
      sbCount('meetings'),
    ])
      .then(([a, m, sd, c]) => {
        setAlerts(a)
        setMunicipalities(m)
        setSchoolDistricts(sd)
        setMeetingCount(c)
      })
      .catch(e => setError(String(e)))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div style={{ color: '#7a7a9a', textAlign: 'center', paddingTop: 80, fontSize: 14 }}>Loading…</div>
  )
  if (error) return (
    <div style={{ color: '#e63946', textAlign: 'center', paddingTop: 80, fontSize: 14, padding: '80px 16px' }}>Error: {error}</div>
  )

  return (
    <>
      <style>{`
        @media (max-width: 600px) {
          .stats-grid { grid-template-columns: 1fr 1fr !important; }
          .muni-table td:last-child, .muni-table th:last-child { display: none; }
        }
      `}</style>

      {/* Hero */}
      <div style={{ marginBottom: 28 }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center',
          background: 'rgba(230,57,70,0.1)', border: '1px solid rgba(230,57,70,0.3)',
          color: '#e63946', fontSize: 11, fontWeight: 700,
          letterSpacing: '0.08em', textTransform: 'uppercase' as const,
          padding: '4px 12px', borderRadius: 100, marginBottom: 10,
        }}>Live Monitor</div>
        <h1 style={{
          fontSize: 'clamp(1.6rem, 5vw, 2.6rem)',
          fontWeight: 900, letterSpacing: '-0.03em', margin: 0, lineHeight: 1.1,
        }}>
          Florida Surveillance Watch{' '}
          <span style={{ color: '#7a7a9a', fontWeight: 400, fontSize: '0.45em', verticalAlign: 'middle', letterSpacing: '0.05em' }}>V1</span>
        </h1>
        <p style={{ color: '#7a7a9a', marginTop: 8, fontSize: 14 }}>
          Monitoring {municipalities.length} FL municipalities and {schoolDistricts.length} school districts for surveillance tech agenda items
        </p>
      </div>

      {/* Stats */}
      <div className="stats-grid" style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: 12, marginBottom: 36,
      }}>
        {[
          { label: 'Cities & Counties',    value: municipalities.length  },
          { label: 'School Districts',     value: schoolDistricts.length },
          { label: 'Meetings Scraped',     value: meetingCount           },
          { label: 'Active Alerts',        value: alerts.length          },
        ].map(s => (
          <div key={s.label} style={{
            background: '#111118', border: '1px solid #1e1e2e',
            borderRadius: 12, padding: '16px 20px',
          }}>
            <div style={{ fontSize: 32, fontWeight: 900, letterSpacing: '-0.03em', color: '#e63946' }}>{s.value}</div>
            <div style={{ fontSize: 12, color: '#7a7a9a', marginTop: 2 }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Alerts */}
      <div style={{ marginBottom: 48 }}>
        <h2 style={{ fontSize: 17, fontWeight: 800, margin: '0 0 14px', letterSpacing: '-0.01em' }}>
          Surveillance Alerts
          {alerts.length > 0 && (
            <span style={{ marginLeft: 10, fontSize: 13, color: '#7a7a9a', fontWeight: 400 }}>{alerts.length} flagged</span>
          )}
        </h2>
        {alerts.length === 0
          ? (
            <div style={{
              color: '#7a7a9a', padding: '32px 16px', textAlign: 'center',
              border: '1px dashed #1e1e2e', borderRadius: 12, fontSize: 14,
            }}>
              No surveillance items detected in upcoming agendas
            </div>
          )
          : alerts.map(m => <AlertCard key={m.meeting_id} meeting={m} />)
        }
      </div>

      {/* Municipalities table */}
      <EntityTable rows={municipalities} label="Monitored Municipalities" />

      {/* School Districts table */}
      <EntityTable rows={schoolDistricts} label="Monitored School Districts" />
    </>
  )
}
