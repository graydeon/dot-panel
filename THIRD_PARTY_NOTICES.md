# Third-party notices and provenance

Dot Panel application source, the portable Worker/authentication adapter, test harness, and original geometric brand assets were authored for this project. They are distributed under AGPL-3.0-only.

No installed dependency tree, private deployment tooling, proprietary platform helper, generated production bundle, or third-party artwork is vendored in this source repository. `package-lock.json` identifies the exact packages used. Dependencies retain their individual license and notice files when installed or redistributed.

Direct runtime dependencies:

| Package | License |
|---|---|
| React | MIT |
| React DOM | MIT |
| Drizzle ORM | Apache-2.0 |

Build/test dependencies include TypeScript (Apache-2.0), Vite (MIT), the Vite React plugin (MIT), esbuild (MIT), Wrangler (MIT/Apache-2.0), Miniflare (MIT), Drizzle Kit (MIT), and the corresponding type packages. Consult each installed package's actual license for its complete terms and any transitive notices before distributing bundled binaries.

The optional brand rendering script imports CairoSVG and Pillow; these are not bundled or required to build the web app. Their respective licenses apply if installed. The SVG wordmark uses original outlined geometric letterforms and no font files.

The GNU AGPL license text in `LICENSE` is the unmodified version 3 text published by the Free Software Foundation at https://www.gnu.org/licenses/agpl-3.0.txt. The license text itself carries the Free Software Foundation's notice.

Protocol references:
- https://developers.openai.com/plugins/build/mcp-events
- https://github.com/standard-webhooks/standard-webhooks
- https://developers.cloudflare.com/workers/runtime-apis/request/

No affiliation or sponsorship by OpenAI or Cloudflare is implied.
