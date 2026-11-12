# Documentation screenshots

The populated light and dark catalog images are reviewed original Compose renders
from [run 42577067647](https://github.com/lambdawalker/android.apexfission.demo-common/actions/runs/42577067647),
artifact `13655369521`, at the exact JitPack 0.1.2 source
`86b43bd7ee858ceb09642ec755f0dc99e7eb5a2f`. The source manifest in the artifact
matches that commit. Maven Central 0.1.2 has the same library and preview sources.
Viewport is 393 × 740 dp, with the fixture host theme and default font scale.
These captures show the released CardTitle without the removed component subtitle
and the App settings action after the cards. The previous images from
`99cdc413f4abd076c4d337d5bca16c38900073b2` predated 0.1.2 and were incorrect.
The checksum file records the original PNGs. These are documentation assets.

Run `./gradlew :demo-common:updateDebugScreenshotTest` to generate new
candidates. Review the originals and update this provenance and checksum
only when intentionally refreshing the documentation.

## Compose API component images

The six standalone card/title images come from reviewed originals in
[run 43155288797](https://github.com/lambdawalker/android.apexfission.demo-common/actions/runs/43155288797),
at PR head `136b77f11ddf602824636eba882381014e5e8b93` and test-merge source
`c0450af6cc2f7952b620ac6ab5c52114a61f89c4`. `DemoCard` and `CardTitle` implementations
are byte-identical to the released 0.1.2 source. These previews are 360 dp wide,
wrap their content and use the fixture host theme at default font scale.
The catalog images above come from the exact release source and show its Settings-button order.
The checksum manifest covers all eight images.
