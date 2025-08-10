import Head from 'next/head'
import ChatWidget from '../components/ChatWidget'

export default function Home() {
  return (
    <div>
      <Head>
        <title>Real-Estate AI Chat Demo</title>
      </Head>
      <main style={{padding:20}}>
        <h1>Real-Estate AI Chat Demo</h1>
        <p>This page contains a floating chat widget for demo purposes.</p>
      </main>
      <ChatWidget />
    </div>
  )
}
