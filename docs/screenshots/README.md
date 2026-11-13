# Documentation screenshots

The light/dark catalog and component images are reviewed originals from
[run 43155288797](https://github.com/lambdawalker/android.apexfission.demo-common/actions/runs/43155288797).
The PR head is `136b77f11ddf602824636eba882381014e5e8b93`; the rendered test-merge
source recorded by the artifact is `c0450af6cc2f7952b620ac6ab5c52114a61f89c4`.

The populated `DemoScreen` viewport is 393 × 740 dp. Standalone `DemoCard`
(both overloads) and `CardTitle` previews are 360 dp wide and wrap their content.
All use the fixture host theme and default font scale. `manifest.json` records
the exact original PNGs. These are documentation assets, not approved comparison
baselines and not files included in published Android artifacts.

The English and Spanish Compose API guides show a light/dark image beside each
component and each card overload. The retained 0.1.2 documentation uses these
same standalone card/title captures, whose implementations are unchanged, but
uses captures from the exact release source to illustrate its own Settings-button
order. Those originals are from run 42577067647 at release commit
`86b43bd7ee858ceb09642ec755f0dc99e7eb5a2f`. The earlier retained catalog images
predated 0.1.2 and have been replaced.

Run `./gradlew :demo-common:updateDebugScreenshotTest` to generate new
candidates. CI renders 11 candidates: populated and empty screens in light/dark,
a narrow large-text screen, and the six standalone component images. Review the
originals and update this provenance and manifest when refreshing documentation. Run `sh ./docs.sh check` to verify the accepted documentation image hashes and dimensions.
